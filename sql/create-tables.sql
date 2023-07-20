
DROP SCHEMA IF EXISTS base CASCADE;

CREATE SCHEMA base AUTHORIZATION adm;


-- ##################################################################
-- #													TYPES																	#
-- ##################################################################


CREATE TYPE base.roles_auth AS ENUM ('SUPERADMIN', 'ADMIN', 'USER');
ALTER TYPE base.roles_auth OWNER TO adm;


CREATE TYPE base.status_auth AS ENUM ('INACTIVE', 'ACTIVE', 'BANNED', 'PENDING');
ALTER TYPE base.status_auth OWNER TO adm;


CREATE TYPE base.notif_type AS ENUM ('ALERT', 'WARNING', 'INFO', 'SUCCESS');
ALTER TYPE base.notif_type OWNER TO adm;


CREATE TYPE base.img_type AS ENUM ('png', 'gif', 'jpg', 'jpeg');
ALTER TYPE base.img_type OWNER TO adm;

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