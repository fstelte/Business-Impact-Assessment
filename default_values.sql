BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "consequence_choices" (
	"id"	INTEGER NOT NULL,
	"choice"	VARCHAR,
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "references" (
	"id"	INTEGER NOT NULL,
	"consequence_category"	VARCHAR,
	"consequence_small"	VARCHAR,
	"consequence_medium"	VARCHAR,
	"consequence_large"	VARCHAR,
	"consequence_huge"	VARCHAR,
	PRIMARY KEY("id")
);
CREATE TABLE IF NOT EXISTS "security_properties" (
	"id"	INTEGER NOT NULL,
	"choice"	VARCHAR,
	PRIMARY KEY("id")
);
INSERT INTO "consequence_choices" ("id","choice") VALUES (1,'Low');
INSERT INTO "consequence_choices" ("id","choice") VALUES (2,'Medium');
INSERT INTO "consequence_choices" ("id","choice") VALUES (3,'High');
INSERT INTO "consequence_choices" ("id","choice") VALUES (4,'Huge');
INSERT INTO "references" ("id","consequence_category","consequence_small","consequence_medium","consequence_large","consequence_huge") VALUES (1,'Financial',NULL,NULL,NULL,NULL);
INSERT INTO "references" ("id","consequence_category","consequence_small","consequence_medium","consequence_large","consequence_huge") VALUES (2,'Operational',NULL,NULL,NULL,NULL);
INSERT INTO "references" ("id","consequence_category","consequence_small","consequence_medium","consequence_large","consequence_huge") VALUES (3,'Regulatory',NULL,NULL,NULL,NULL);
INSERT INTO "references" ("id","consequence_category","consequence_small","consequence_medium","consequence_large","consequence_huge") VALUES (4,'Reputation and Trust',NULL,NULL,NULL,NULL);
INSERT INTO "references" ("id","consequence_category","consequence_small","consequence_medium","consequence_large","consequence_huge") VALUES (5,'Human and Safety',NULL,NULL,NULL,NULL);
INSERT INTO "references" ("id","consequence_category","consequence_small","consequence_medium","consequence_large","consequence_huge") VALUES (6,'Privacy',NULL,NULL,NULL,NULL);
INSERT INTO "security_properties" ("id","choice") VALUES (1,'Confidentiallity');
INSERT INTO "security_properties" ("id","choice") VALUES (2,'Integrity');
INSERT INTO "security_properties" ("id","choice") VALUES (3,'Availability');
COMMIT;
