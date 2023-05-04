CREATE TABLE algo_trader.brokers
(
    id serial NOT NULL,
    broker_name character varying(45) NOT NULL,
    broker_id character varying(15) NOT NULL,
    password character varying(100),
    user_name character varying(8) NOT NULL,
    totp_key character varying(32),
    auto_login boolean,
    status character varying(20),
    broker_addition_date bigint,
    last_login_date bigint,
    app_key character varying(150),
    secret_key character varying(150),
    PRIMARY KEY (id),
    CONSTRAINT broker_id_pk UNIQUE (broker_id)
);

ALTER TABLE IF EXISTS algo_trader.brokers
    OWNER to postgres;