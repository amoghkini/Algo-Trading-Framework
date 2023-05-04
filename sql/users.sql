CREATE TABLE algo_trader.users
(
    id serial NOT NULL,
    email_id character varying(45) NOT NULL,
    password character varying(100) NOT NULL,
    first_name character varying(40),
    middle_name character varying(40),
    last_name character varying(40),
    user_name character varying(8) NOT NULL,
    account_creation_date bigint NOT NULL,
    account_status character varying(20) NOT NULL,
    last_login_date bigint,
    profile_pic character varying(100),
    mobile_no character varying(10) NOT NULL,
    date_of_birth date,
    address1 character varying(45),
    address2 character varying(45),
    address3 character varying(45),
    city character varying(20),
    state character varying(20),
    country character varying(20),
    pin_code integer,
    PRIMARY KEY (id),
    CONSTRAINT email_id_pk UNIQUE (email_id),
    CONSTRAINT mobile_no_pk UNIQUE (mobile_no)
);

ALTER TABLE IF EXISTS algo_trader.users
    OWNER to postgres;