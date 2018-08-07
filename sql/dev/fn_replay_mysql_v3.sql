﻿-- fn_replay_mysql_v3.sql
CREATE OR REPLACE FUNCTION sch_chameleon.fn_replay_mysql_blocks(integer,integer,boolean)
RETURNS sch_chameleon.ty_replay_status AS
$BODY$
	DECLARE
		p_i_max_events		ALIAS FOR $1;
		p_i_id_source		ALIAS FOR $2;
		p_b_exit_on_error	ALIAS FOR $3;
		v_ty_status		sch_chameleon.ty_replay_status;
		v_r_statements		record;
		v_i_id_batch		bigint;
		v_v_log_table		text;
		v_t_ddl			text;
		v_t_main_sql		text;
		v_i_replayed		integer;
		v_i_skipped		integer;
		v_i_ddl			integer;
		v_i_evt_replay		bigint[];
		v_i_evt_queue		bigint[];
		v_ts_evt_source		timestamp without time zone;
		v_tab_enabled		boolean;

	BEGIN
		v_i_replayed:=0;
		v_i_ddl:=0;
		v_i_skipped:=0;
		
		RAISE DEBUG 'Searching batches to replay for source id: %', p_i_id_source;
		v_i_id_batch:= (
			SELECT 
				bat.i_id_batch 
			FROM 
				sch_chameleon.t_replica_batch bat
				INNER JOIN  sch_chameleon.t_batch_events evt
				ON
					evt.i_id_batch=bat.i_id_batch
			WHERE 
					bat.b_started 
				AND	bat.b_processed 
				AND	NOT bat.b_replayed
				AND	bat.i_id_source=p_i_id_source
			ORDER BY 
				bat.ts_created 
			LIMIT 1
			)
		;

		v_v_log_table:=(
			SELECT 
				v_log_table
			FROM 
				sch_chameleon.t_replica_batch 
			WHERE 
				i_id_batch=v_i_id_batch
			)
		;
		IF v_i_id_batch IS NULL 
		THEN
			RAISE DEBUG 'There are no batches available for replay';
			RETURN v_ty_status;
		END IF;
		
		RAISE DEBUG 'Found id_batch %, data in log table %', v_i_id_batch,v_v_log_table;
		v_i_evt_replay:=(
			SELECT 
				i_id_event[1:p_i_max_events] 
			FROM 
				sch_chameleon.t_batch_events 
			WHERE 
				i_id_batch=v_i_id_batch
		);
		
		RAISE DEBUG 'Building a list of event id with max length %...', p_i_max_events;
		v_i_evt_queue:=(
			SELECT 
				i_id_event[p_i_max_events+1:array_length(i_id_event,1)] 
			FROM 
				sch_chameleon.t_batch_events 
			WHERE 
				i_id_batch=v_i_id_batch
		);
		RAISE DEBUG 'got: % ',v_i_evt_queue;
		RAISE DEBUG 'Finding the last executed event''s timestamp...';
		v_ts_evt_source:=(
			SELECT 
				to_timestamp(i_my_event_time)
			FROM	
				sch_chameleon.t_log_replica
			WHERE
					i_id_event=v_i_evt_replay[array_length(v_i_evt_replay,1)]
				AND	i_id_batch=v_i_id_batch
		);
		RAISE DEBUG 'got %',v_ts_evt_source;
		RAISE DEBUG 'Generating the main loop sql';

		v_t_main_sql:=format('
			SELECT 
				array_agg(i_id_event) AS i_id_event,
				count(enm_binlog_event) FILTER (WHERE enm_binlog_event = ''ddl'') as i_ddl,
				count(enm_binlog_event) FILTER (WHERE enm_binlog_event <> ''ddl'') as i_replayed,
				
				v_table_name,
				v_schema_name,
				string_agg(
				CASE
					WHEN enm_binlog_event = ''ddl''
					THEN 
						t_query
					WHEN enm_binlog_event = ''insert''
					THEN
						format(
							''INSERT INTO %%I.%%I %%s;'',
							v_schema_name,
							v_table_name,
							t_dec_data
							
						)
					WHEN enm_binlog_event = ''update''
					THEN
						format(
							''UPDATE %%I.%%I SET %%s WHERE %%s;'',
							v_schema_name,
							v_table_name,
							t_dec_data,
							t_pk_data
						)
					WHEN enm_binlog_event = ''delete''
					THEN
						format(
							''DELETE FROM %%I.%%I WHERE %%s;'',
							v_schema_name,
							v_table_name,
							t_pk_data
						)
					
				END,'' '') AS t_sql
			FROM 
			(
				SELECT 
					dec.i_id_event,
					dec.v_table_name,
					dec.v_schema_name,
					dec.enm_binlog_event,
					dec.t_query as t_query,
					dec.ts_event_datetime,
					CASE
						WHEN dec.enm_binlog_event = ''insert''
						THEN
						format(''(%%s) VALUES (%%s)'',string_agg(format(''%%I'',dec.t_column),'',''),string_agg(format(''%%L'',jsb_event_after->>t_column),'',''))
						WHEN dec.enm_binlog_event = ''update''
						THEN
							string_agg(format(''%%I=%%L'',dec.t_column,jsb_event_after->>t_column),'','')
						
					END AS t_dec_data,
					string_agg(DISTINCT format(
								''%%I=%%L'',
								dec.v_table_pkey,
								CASE 
									WHEN dec.enm_binlog_event = ''update''
									THEN
										jsb_event_before->>v_table_pkey
									ELSE
										jsb_event_after->>v_table_pkey
								END 	
							),'','') as  t_pk_data
				FROM 
				(
					SELECT 
						log.i_id_event,
						log.v_table_name,
						log.v_schema_name,
						log.enm_binlog_event,
						coalesce(log.jsb_event_after,''{"foo":"bar"}''::jsonb) as jsb_event_after,
						(jsonb_each_text(coalesce(log.jsb_event_after,''{"foo":"bar"}''::jsonb))).key AS t_column,
						log.jsb_event_before,
						log.t_query as t_query,
						log.ts_event_datetime,
						unnest(v_table_pkey) as v_table_pkey
					FROM 
						sch_chameleon.%I log
						INNER JOIN sch_chameleon.t_replica_tables tab
							ON 
									tab.v_table_name=log.v_table_name
								AND	tab.v_schema_name=log.v_schema_name
					WHERE
							tab.b_replica_enabled
						AND	i_id_event = ANY(%L)
				) dec
				GROUP BY 
					dec.i_id_event,
					dec.v_table_name,
					dec.v_schema_name,
					dec.enm_binlog_event,
					dec.t_query,
					dec.ts_event_datetime
			) par
			GROUP BY 	
				v_table_name,
				v_schema_name
			;
		
		',v_v_log_table,v_i_evt_replay);
		--RAISE DEBUG 'Generated SQL: %', v_t_main_sql;
		FOR v_r_statements IN EXECUTE v_t_main_sql
		LOOP
			RAISE DEBUG 'Replaying data for table %.%', v_r_statements.v_schema_name,v_r_statements.v_table_name;
			BEGIN
				EXECUTE v_r_statements.t_sql;
				v_i_ddl:=v_i_ddl+v_r_statements.i_ddl;
				v_i_replayed:=v_i_replayed+v_r_statements.i_replayed;
					
				
			EXCEPTION
				WHEN OTHERS
				THEN
				RAISE NOTICE 'An error occurred when replaying data for the table %.%',v_r_statements.v_schema_name,v_r_statements.v_table_name;
				RAISE NOTICE 'SQLSTATE: % - ERROR MESSAGE %',SQLSTATE, SQLERRM;
				RAISE NOTICE 'The table %.% has been removed from the replica',v_r_statements.v_schema_name,v_r_statements.v_table_name;
				UPDATE sch_chameleon.t_replica_tables 
					SET b_replica_enabled=False 
				WHERE 
						v_table_name=v_r_statements.v_table_name
					AND	v_schema_name=v_r_statements.v_schema_name
				;
				v_ty_status.v_table_error:=array_append(v_ty_status.v_table_error, format('%I.%I SQLSTATE: %s - ERROR MESSAGE: %s',v_r_statements.v_schema_name,v_r_statements.v_table_name,SQLSTATE, SQLERRM)::character varying) ;
				RAISE NOTICE 'Adding error log entry for table %.% ',v_r_statements.v_schema_name,v_r_statements.v_table_name;
			END;
		END LOOP;
		
		
		RETURN v_ty_status;
	END;
	
$BODY$
LANGUAGE plpgsql;
