CREATE TABLE algo_trader.access_tokens
(
    broker_id character varying(15) NOT NULL,
    token_date date NOT NULL,
    broker_name character varying(45) NOT NULL,
    access_token character varying(200) NOT NULL,
    PRIMARY KEY (broker_id, token_date)
);

ALTER TABLE IF EXISTS algo_trader.access_tokens
    OWNER to postgres;