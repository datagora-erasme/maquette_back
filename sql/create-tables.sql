
DROP SCHEMA IF EXISTS base CASCADE;

CREATE SCHEMA base AUTHORIZATION adm;


-- ##################################################################
-- #													TYPES																	#
-- ##################################################################


CREATE TYPE base.roles_auth AS ENUM ('SUPERADMIN', 'ADMIN', 'USER');
ALTER TYPE base.roles_auth OWNER TO adm;


CREATE TYPE base.status_auth AS ENUM ('INACTIVE', 'ACTIVE', 'BANNED', 'PENDING');
ALTER TYPE base.status_auth OWNER TO adm;


CREATE TYPE base.type_notif AS ENUM ('ALERT', 'WARNING', 'INFO', 'SUCCESS');
ALTER TYPE base.type_notif OWNER TO adm;


CREATE TYPE base.notif_type AS ENUM ('ALERT', 'WARNING', 'INFO', 'SUCCESS');
ALTER TYPE base.notif_type OWNER TO adm;


CREATE TYPE base.img_type AS ENUM ('png', 'gif', 'jpg', 'jpeg');
ALTER TYPE base.img_type OWNER TO adm;

CREATE TYPE base.customer_status AS ENUM ('PREPARATION', 'STEP_1', 'STEP_2', 'END_MISSION', 'INACTIVE', 'ARCHIVED');
ALTER TYPE base.customer_status OWNER TO adm;

-- ##################################################################
-- #													TABLES																#
-- ##################################################################


CREATE TABLE base.avatars (
	id serial PRIMARY KEY,
	type base.img_type NOT NULL,
  file_name character varying(100) NOT NULL,
  data text NOT NULL
);
ALTER TABLE base.avatars OWNER TO adm;

CREATE TABLE base.authentications (
	id serial PRIMARY KEY,
	email character varying(255) NOT NULL UNIQUE,
	password character varying(255) NOT NULL,
	role base.roles_auth NOT NULL DEFAULT 'USER'::base.roles_auth,
	status base.status_auth NOT NULL DEFAULT 'ACTIVE'::base.status_auth
);
ALTER TABLE base.authentications OWNER TO adm;

CREATE TABLE base.users (
	id serial PRIMARY KEY,
	date_create timestamp without time zone NOT NULL DEFAULT now(),
	date_archived TIMESTAMP WITHOUT TIME ZONE NULL DEFAULT NULL,
	firstname character varying(100) NOT NULL,
	lastname character varying(100) NOT NULL,
	phone character varying(100) NULL,
	avatar_id INT,
	authentication_id INT,
	FOREIGN KEY (avatar_id)
		REFERENCES base.avatars (id) MATCH SIMPLE
		ON UPDATE NO ACTION
		ON DELETE NO ACTION,
	FOREIGN KEY (authentication_id)
		REFERENCES base.authentications (id) MATCH SIMPLE
		ON UPDATE NO ACTION
		ON DELETE NO ACTION
);
ALTER TABLE base.users OWNER TO adm;

CREATE TABLE base.notifications (
	id serial PRIMARY KEY,
	date_create timestamp without time zone NOT NULL DEFAULT now(),
	title character varying(255) NOT NULL,
	type base.type_notif NOT NULL,
	content character varying(255) NOT NULL,
	link character varying(255) NULL DEFAULT NULL,
	user_id INTEGER NULL,
	FOREIGN KEY (user_id)
		REFERENCES base.users (id) MATCH SIMPLE
		ON UPDATE NO ACTION
		ON DELETE NO ACTION
);
ALTER TABLE base.notifications OWNER TO adm;

CREATE TABLE base.documents (
	id serial PRIMARY KEY,
	date_create timestamp without time zone NOT NULL DEFAULT now(),
	type character varying(255) NOT NULL,
	title character varying(255) NOT NULL,
	file_name character varying(255) NOT NULL,
	data text NOT NULL,
	user_id INT NOT NULL,
	FOREIGN KEY (user_id)
		REFERENCES base.users (id) MATCH SIMPLE
		ON UPDATE NO ACTION
		ON DELETE NO ACTION
);
ALTER TABLE base.documents OWNER TO adm;

CREATE TABLE base.customers (
	id SERIAL PRIMARY KEY,
	date_create TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
	date_archived TIMESTAMP WITHOUT TIME ZONE NULL DEFAULT NULL,
	name CHARACTER VARYING(100) NOT NULL,
	status base.customer_status NOT NULL DEFAULT 'PREPARATION'::base.customer_status,
	is_individual BOOLEAN NOT NULL,
	siret CHARACTER VARYING(17) NULL DEFAULT NULL,
	tva_code CHARACTER VARYING(15) NULL DEFAULT NULL,
	office_phone CHARACTER VARYING(20) NULL DEFAULT NULL,
	office_address CHARACTER VARYING(100) NOT NULL,
	office_address_comp CHARACTER VARYING(100) NULL DEFAULT NULL,
	office_postal_code CHARACTER VARYING(10) NOT NULL,
	office_city CHARACTER VARYING(100) NOT NULL,
	user_id INT NULL DEFAULT NULL,
	FOREIGN KEY (user_id)
		REFERENCES base.users (id) MATCH SIMPLE
		ON UPDATE NO ACTION
		ON DELETE NO ACTION
);
ALTER TABLE base.customers OWNER TO adm;


CREATE TABLE base.contacts (
	id SERIAL PRIMARY KEY,
	date_create TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
	firstname CHARACTER VARYING(100) NOT NULL,
	lastname CHARACTER VARYING(100) NOT NULL,
	email CHARACTER VARYING(100) NOT NULL,
	phone CHARACTER VARYING(20) NULL,
	job_title CHARACTER VARYING(100) NOT NULL
);
ALTER TABLE base.contacts OWNER TO adm;

CREATE TABLE base.notifications_users (
	id serial PRIMARY KEY,
	is_viewed BOOLEAN NULL DEFAULT false,
	user_id INT NOT NULL,
	FOREIGN KEY (user_id)
		REFERENCES base.users (id) MATCH SIMPLE
		ON UPDATE NO ACTION
		ON DELETE NO ACTION,
	notification_id INT NOT NULL,
	FOREIGN KEY (notification_id)
		REFERENCES base.notifications (id) MATCH SIMPLE
		ON UPDATE NO ACTION
		ON DELETE CASCADE
);
ALTER TABLE base.notifications_users OWNER TO adm;

CREATE TABLE base.customers_contacts (
	id SERIAL PRIMARY KEY,
	customer_id INT NOT NULL,
	FOREIGN KEY (customer_id)
		REFERENCES base.customers (id) MATCH SIMPLE
		ON UPDATE NO ACTION
		ON DELETE NO ACTION,
	contact_id INT NOT NULL,
	FOREIGN KEY (contact_id)
		REFERENCES base.contacts (id) MATCH SIMPLE
		ON UPDATE NO ACTION
		ON DELETE CASCADE
);
ALTER TABLE base.customers_contacts OWNER TO adm;

CREATE TABLE base.customers_documents (
	id SERIAL PRIMARY KEY,
	customer_id INT NOT NULL,
	FOREIGN KEY (customer_id)
		REFERENCES base.customers (id) MATCH SIMPLE
		ON UPDATE NO ACTION
		ON DELETE NO ACTION,
	document_id INT NULL DEFAULT NULL,
	FOREIGN KEY (document_id)
		REFERENCES base.documents (id) MATCH SIMPLE
		ON UPDATE NO ACTION
		ON DELETE NO ACTION
);
ALTER TABLE base.customers_documents OWNER TO adm;

