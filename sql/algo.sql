CREATE TABLE algo_trader.algo
(
    name character varying(20) NOT NULL,
    status character varying(20) NOT NULL,
    start_time bigint,
    end_time bigint,
    algo_start_reason character varying(50),
    algo_stop_reason character varying(50),
    PRIMARY KEY (name)
);

ALTER TABLE IF EXISTS algo_trader.algo
    OWNER to postgres;