
DROP SCHEMA IF EXISTS base CASCADE;

CREATE SCHEMA base AUTHORIZATION adm;


-- ##################################################################
-- #													TYPES																	#
-- ##################################################################


CREATE TYPE base.roles_auth AS ENUM ('SUPERADMIN', 'ADMIN', 'USER');
ALTER TYPE base.roles_auth OWNER TO adm;


CREATE TYPE base.status_auth AS ENUM ('INACTIVE', 'ACTIVE', 'BANNED', 'PENDING');
ALTER TYPE base.status_auth OWNER TO adm;

CREATE TYPE base.img_type AS ENUM ('png', 'gif', 'jpg', 'jpeg');
ALTER TYPE base.img_type OWNER TO adm;

-- ##################################################################
-- #													TABLES																#
-- ##################################################################



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
	authentication_id INT,
	FOREIGN KEY (authentication_id)
		REFERENCES base.authentications (id) MATCH SIMPLE
		ON UPDATE NO ACTION
		ON DELETE NO ACTION
);
ALTER TABLE base.users OWNER TO adm;

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

CREATE TABLE base.projects (
	id serial PRIMARY KEY,
	date_create timestamp without time zone NOT NULL DEFAULT now(),
	name character varying(100) NOT NULL,
	bbox character varying(1000) NOT NULL,
	nb_plaques_h INT NOT NULL ,
	nb_plaques_v INT NOT NULL ,
	ratio INT NOT NULL,
	user_id INTEGER NULL,
	FOREIGN KEY (user_id)
		REFERENCES base.users (id) MATCH SIMPLE
		ON UPDATE NO ACTION
		ON DELETE NO ACTION,
	model_id INTEGER NULL,
	FOREIGN KEY (model_id)
		REFERENCES base.documents (id) MATCH SIMPLE
		ON UPDATE NO ACTION
		ON DELETE NO ACTION,
	csv_id INTEGER NULL,
	FOREIGN KEY (csv_id)
		REFERENCES base.documents (id) MATCH SIMPLE
		ON UPDATE NO ACTION
		ON DELETE NO ACTION,
	emprise_id INTEGER NULL,
	FOREIGN KEY (emprise_id)
		REFERENCES base.documents (id) MATCH SIMPLE
		ON UPDATE NO ACTION
		ON DELETE NO ACTION
);
ALTER TABLE base.projects OWNER TO adm;

CREATE TABLE base.datas (
	id serial PRIMARY KEY,
	name character varying(100) NOT NULL,
	service character varying(100) NULL,
	url character varying(100) NULL,
	layername character varying(100) NULL,
	srsname character varying(100) NULL,
	style character varying(100) NULL,
	version character varying(100) NULL,
	only_url BOOLEAN NULL DEFAULT false,
	project_id INTEGER NULL,
	FOREIGN KEY (project_id)
		REFERENCES base.projects (id) MATCH SIMPLE
		ON UPDATE NO ACTION
		ON DELETE NO ACTION
);
ALTER TABLE base.datas OWNER TO adm;