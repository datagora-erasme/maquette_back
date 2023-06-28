import json
import unittest
import sys
import os
import pytest
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    DateTime,
    Text,
    ForeignKey,
)
from sqlalchemy.engine import URL
from sqlalchemy.orm import declarative_base, sessionmaker
import random
import string

#                                                              USERS
#                                                                                                      +-----------------------------------+
#                                                                                                      |                                   |
#              +---------------------------------+                                                     |                                   |
#              |                                 |                                                     |                                   |
#              |                                 |                                                     |                                   |
#          +--->  Creates Authentication ID      +----------------------------------------------------->         Delete User + Auth ID     |
#          |   |                                 |                                                     |                                   |
#          |   |                                 |                                                     |                                   |
#          |   +---------------------------------+                                                     |                                   |
#          |                                                                                           +-------------------^---------------+
#          |                                                                                                               |
#          |                                                                                                               |
#          |                                                                                                               |
# +--------+---------+            +--------------------+           +-----------------+         +---------------------------+------------+
# |                  |            |                    |           |                 |         |                                        |
# |      Create      +-----ID---->|   Fetch by ID      +----ID---->|   Patch by ID   +---ID---->      List all + contains ID*           |
# |                  |            |                    |           |                 |         |                                        |
# +------------------+            +--------------------+           +-----------------+         +----------------------------------------+
#
#


#                                                                                                   Auth ID
#
#                 +--------------------------------------------------------------------------------------Email---------------------------------------------------------------------------------------------+
#                 |                                                                                                                                                                                        |
#                 |                                                                                                                                                                                        |
#                 |                                                                                                                                                                                        |
#                 |                                                                                                                                                                                        |
#                 |                                                                                                                                                                                        |
#                 |                                                                                                                                                                                        |
#                 |                                                                                                                                                                                        |
#                 |                                                                                                                                                                                        |
#                 |                                                                                                                                                                                        |
#                 |                                                                                                                                                                                        |
#                 |                                                                                                                                                                                        |
#                 |                                                                                                                                                                                        |
# +---------------+---------------+             +------------------------+                   +---------------------------+                  +-----------------------------+               +----------------v------------------+
# |                               |             |                        |                   |                           |                  |                             |               |                                   |
# |    Auth ID Creation using     |             |                        |                   |   List all Auth IDs       |                  |                             |               |                                   |
# |                               |             |                        |                   |                           |                  |                             |               |                                   |
# |            Email              +-----ID------>    Fetch by Auth ID    +--------ID--------->           &               +--------ID-------->       Delete Auth ID        |               | Password Reset using Auth ID Email|
# |                               |             |                        |                   |   contains new Auth ID    |                  |                             |               |                                   |
# |                               |             |                        |                   |                           |                  |                             |               |                                   |
# +-------------------------------+             +------------------------+                   +---------------------------+                  +-----------------------------+               |                                   |
#                                                                                                                                                                                         +-----------------------------------+


from dotenv import load_dotenv

load_dotenv()
url = URL.create(
    drivername=os.getenv("BDD_DB_SYSTEM"),
    host=os.getenv("BDD_CONFIG_HOST"),
    username=os.getenv("BDD_CONFIG_USER"),
    password=os.getenv("BDD_CONFIG_PASSWD"),
    database=os.getenv("BDD_CONFIG_DB"),
    port=os.getenv("BDD_CONFIG_PORT"),
)

engine = create_engine(url)
Session = sessionmaker(bind=engine)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from app import db
import app as tested_app

adminAcct = {"login": "x.thiermant@exo-dev.fr", "password": "!Ex0D3v!"}

Base = declarative_base()


def random_char(char_num):
    return "".join(random.choice(string.ascii_letters) for _ in range(char_num))


class BoilerplateTest(unittest.TestCase):
    def setUp(self):
        tested_app.app.config["TESTING"] = True
        self.app = tested_app.app.test_client()
        # Base.metadata.create_all(engine) // no need for the momeny !
        self.session = Session()

    # # Utils # #

    def get_token(self):
        # get Token for next tests
        r = self.app.post(
            "/api/auth/login",
            content_type="application/json",
            data=json.dumps(adminAcct),
        )
        res = r.json["token"]
        headers = {"Authorization": f"Bearer {res}"}
        return headers

    def get_auth_id(self):
        header = self.get_token()
        payload = {
            "email": random_char(7).lower() + "@exo-dev.fr",
            "role": "SUPERADMIN",
        }
        r = self.app.post(
            "/api/auth",
            content_type="application/json",
            headers=header,
            data=json.dumps(payload),
        )
        if r.status_code == 200:
            # For global usage
            global newuserId
            newuserId = r.json["id"]
            return newuserId
        else:
            raise ValueError(r)

    # # Default Routes test # #

    # Status
    def test_status(self):
        r = self.app.get("/api/core/status")
        self.assertIn(b"Running", r.data)

    # Login Test # #

    # Sucess
    def test_login(self):
        r = self.app.post(
            "/api/auth/login",
            content_type="application/json",
            data=json.dumps(adminAcct),
        )
        self.assertEqual(r.status_code, 200)

    # Fail
    def test_fail_login(self):
        payload = {"login": "xthiermant", "password": "toto"}
        r = self.app.post(
            "/api/auth/login", content_type="application/json", data=json.dumps(payload)
        )
        self.assertEqual(r.status_code, 400)

    # Auth Test # #

    # Auth ID Creation Test
    def test_auth_id_creation(self):
        header = self.get_token()
        global usedmail
        usedmail = random_char(7).lower() + "@exo-dev.fr"
        payload = {"email": usedmail, "role": "SUPERADMIN"}
        r = self.app.post(
            "/api/auth",
            content_type="application/json",
            headers=header,
            data=json.dumps(payload),
        )
        if r.status_code == 200:
            # For global usage
            global testid
            testid = r.json["id"]
            self.assertEqual(r.status_code, 200)
        else:
            raise ValueError(r)

    # Fetch by Auth ID Test
    def test_auth_id_fetch(self):
        header = self.get_token()
        r = self.app.get("/api/auth/" + str(testid), headers=header)
        self.assertEqual(r.status_code, 200)

    # List all auth IDs Test
    def test_auth_id_list(self):
        header = self.get_token()
        r = self.app.get("/api/auth", headers=header)
        self.assertEqual(r.status_code, 200)

    # Delete Auth ID Test
    @pytest.mark.order(-1)
    def test_auth_id_delete(self):
        header = self.get_token()
        r = self.app.delete(
            "/api/auth/" + str(testid), content_type="application/json", headers=header
        )
        self.assertEqual(r.status_code, 200)

    # Password reset Test
    def test_password_reset(self):
        header = self.get_token()
        r = self.app.post(
            "/api/auth/reset",
            content_type="application/json",
            headers=header,
            data=json.dumps({"email": usedmail}),
        )
        self.assertEqual(r.status_code, 200)

    # Users Test # #

    # User Creation Test

    def test_user_creation(self):
        header = self.get_token()
        auth_id = self.get_auth_id()
        payload = {
            "authentication_id": auth_id,
            "firstname": "Sofiane",
            "lastname": "Hamlaoui",
        }
        # For global usage
        global newuser
        r = self.app.post(
            "/api/users",
            content_type="application/json",
            headers=header,
            data=json.dumps(payload),
        )
        newuser = r.json["id"]
        self.assertEqual(r.status_code, 200)

    # User Fetch Test
    def test_user_fetch(self):
        header = self.get_token()

        r = self.app.get(
            "/api/users",
            content_type="application/json",
            headers=header,
            data=json.dumps({"id": newuser}),
        )
        self.assertEqual(r.status_code, 200)

    # User Patch Test
    def test_user_patch(self):
        header = self.get_token()

        r = self.app.patch(
            "/api/users/" + str(newuser),
            content_type="application/json",
            headers=header,
            data=json.dumps(
                {"id": newuser, "firstname": "SofianePatch2", "lastname": "LastPatch2"}
            ),
        )
        self.assertEqual(r.status_code, 200)

    # List all users Test
    def test_list_allusers(self):
        header = self.get_token()

        r = self.app.get("/api/users", headers=header)
        self.assertEqual(r.status_code, 200)

    # Delete user Test
    @pytest.mark.order(-2)
    def test_user_delete(self):
        header = self.get_token()
        r = self.app.delete("/api/users/" + str(newuser), headers=header)
        self.assertEqual(r.status_code, 200)

    # Notifications Test # #

    def test_list_allnotifs(self):
        header = self.get_token()

        r = self.app.get("/api/notifications", headers=header)
        self.assertEqual(r.status_code, 200)

    def test_create_notif(self):
        header = self.get_token()
        global newnotif
        r = self.app.post(
            "/api/notifications",
            content_type="application/json",
            headers=header,
            data=json.dumps(
                {
                    "title": "Notif Title",
                    "type": "WARNING",
                    "content": "Random Content",
                    "link": "https://notifExoDev",
                }
            ),
        )
        newnotif = r.json["id"]
        self.assertEqual(r.status_code, 200)

    @pytest.mark.order(-3)
    def test_delete_notif(self):
        header = self.get_token()
        r = self.app.delete("/api/notifications/" + str(newnotif), headers=header)
        self.assertEqual(r.status_code, 200)

    def test_patch_notif(self):
        header = self.get_token()
        r = self.app.patch(
            "/api/notifications/" + str(newnotif),
            content_type="application/json",
            headers=header,
            data=json.dumps(
                {
                    "title": "Notif Title Patch",
                    "type": "WARNING",
                    "content": "Random ContentPatch",
                    "link": "https://notifExoDevPatch",
                }
            ),
        )
        self.assertEqual(r.status_code, 200)

    # Documents Test # #

    def test_list_all_docs(self):
        header = self.get_token()

        r = self.app.get("/api/documents", headers=header)
        self.assertEqual(r.status_code, 200)

    def test_create_doc(self):
        header = self.get_token()
        global newdoc
        r = self.app.post(
            "/api/documents",
            content_type="application/json",
            headers=header,
            data=json.dumps(
                {
                    "data": "Random",
                    "file_name": "doc.pdf",
                    "title": "Top Secret",
                    "type": "pdf",
                }
            ),
        )
        newdoc = r.json["id"]
        self.assertEqual(r.status_code, 200)

    @pytest.mark.order(-4)
    def test_delete_doc(self):
        header = self.get_token()
        r = self.app.delete("/api/documents/" + str(newdoc), headers=header)
        self.assertEqual(r.status_code, 200)

    def test_info_doc(self):
        header = self.get_token()
        r = self.app.get("/api/documents/" + str(newdoc), headers=header)
        self.assertEqual(r.status_code, 200)

    def test_patch_doc(self):
        header = self.get_token()
        r = self.app.patch(
            "/api/documents/" + str(newdoc),
            content_type="application/json",
            headers=header,
            data=json.dumps(
                {
                    "data": "Random",
                    "file_name": "doc.pdf",
                    "title": "Top Secret Patch",
                    "type": "pdf",
                }
            ),
        )
        self.assertEqual(r.status_code, 200)

    # Customers Test # #

    def test_list_allcustomers(self):
        header = self.get_token()

        r = self.app.get("/api/customers/select", headers=header)
        self.assertEqual(r.status_code, 200)

    def test_create_customer(self):
        header = self.get_token()
        global newcustomer
        r = self.app.post(
            "/api/customers",
            content_type="application/json",
            headers=header,
            data=json.dumps(
                {
                    "is_individual": True,
                    "naf_code": "6654",
                    "name": "Exo-Dev",
                    "office_address": "Lyon",
                    "office_address_comp": "Lyon",
                    "office_city": "Lyon",
                    "office_phone": "033156454",
                    "office_postal_code": "69000",
                    "siret": "654645",
                    "status": "ARCHIVED",
                    "tva_code": "4231",
                    "user_id": 1,
                }
            ),
        )
        newcustomer = r.json["id"]
        self.assertEqual(r.status_code, 200)

    def test_info_customer(self):
        header = self.get_token()
        r = self.app.get("/api/customers/" + str(newcustomer), headers=header)
        self.assertEqual(r.status_code, 200)

    def test_patch_customer(self):
        header = self.get_token()
        r = self.app.patch(
            "/api/customers/" + str(newcustomer),
            content_type="application/json",
            headers=header,
            data=json.dumps(
                {
                    "is_individual": "true",
                    "naf_code": "6654",
                    "name": "Exo-Dev Patch",
                    "office_address": "Lyon",
                    "office_address_comp": "Lyon",
                    "office_city": "Lyon",
                    "office_phone": "033156454",
                    "office_postal_code": "69000",
                    "siret": "654645",
                    "status": "ARCHIVED",
                    "tva_code": "4231",
                    "user_id": 1,
                }
            ),
        )
        self.assertEqual(r.status_code, 200)

    @pytest.mark.order(-5)
    def test_delete_customer(self):
        header = self.get_token()
        r = self.app.delete("/api/customers/" + str(newcustomer), headers=header)
        self.assertEqual(r.status_code, 200)

    def test_list_allcontacts(self):
        header = self.get_token()

        r = self.app.get("/api/contacts", headers=header)
        self.assertEqual(r.status_code, 200)

    @pytest.mark.order(after="test_create_customer")
    def test_create_contact(self):
        header = self.get_token()
        global newcontact
        r = self.app.post(
            "/api/contacts/customers",
            content_type="application/json",
            headers=header,
            data=json.dumps(
                {
                    "customer_id": newcustomer,
                    "email": "s.hamlaoui@exo-dev.fr",
                    "firstname": "Sofiane",
                    "job_title": "DevOps",
                    "lastname": "Elon",
                    "phone": "+33119",
                }
            ),
        )
        newcontact = r.json["id"]
        self.assertEqual(r.status_code, 200)

    def test_info_contact(self):
        header = self.get_token()
        r = self.app.get("/api/contacts/" + str(newcontact), headers=header)
        self.assertEqual(r.status_code, 200)

    @pytest.mark.order(after="test_create_contact")
    def test_patch_contact(self):
        header = self.get_token()
        r = self.app.patch(
            "/api/contacts/" + str(newcontact),
            content_type="application/json",
            headers=header,
            data=json.dumps(
                {
                    "customer_id": newcustomer,
                    "email": "LYON Patch",
                    "firstname": "LYON Patch",
                    "job_title": "LYON Patch",
                    "lastname": "LYON Patch",
                    "phone": "LYON Patch",
                }
            ),
        )
        self.assertEqual(r.status_code, 200)

    @pytest.mark.order(-6)
    def test_delete_contact(self):
        header = self.get_token()
        r = self.app.delete("/api/contacts/" + str(newcontact), headers=header)
        self.assertEqual(r.status_code, 200)


if __name__ == "__main__":
    unittest.main()
