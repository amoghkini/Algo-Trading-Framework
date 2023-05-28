CREATE TABLE algo_trader.strategies
(
    id serial NOT NULL,
    username character varying(8) NOT NULL,
    name character varying(30) NOT NULL,
    product_type character varying(10) NOT NULL,
    start_timestamp time without time zone NOT NULL,
    stop_timestamp time without time zone NOT NULL,
    square_off_timestamp time without time zone NOT NULL,
    target_percentage numeric,
    stop_loss_percentage numeric,
    capital integer NOT NULL,
    leverage smallint,
    max_trades_per_day smallint,
    is_fno boolean,
    capital_per_set integer,
    PRIMARY KEY (id)
);

ALTER TABLE IF EXISTS algo_trader.strategies
    OWNER to postgres;


-- Sample insert query
INSERT INTO algo_trader.strategies 
(username, name, product_type, start_timestamp, stop_timestamp, square_off_timestamp, target_percentage, stop_loss_percentage, capital, leverage, max_trades_per_day, is_fno, capital_per_set)
VALUES 
('amogh_ap', 'SAMPLE', 'MIS', '09:30:00', '14:30:00', '15:00:00',2.2, 1.2, 3000, 1, 3, false, 0);