header_mail_template = """
<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="content-type" content="text/html; charset=UTF-8">
  <title>{0}</title>
</head>
<body style="font-family: Calibri; background-color:white;">
  <div style="margin:auto;width:100%;max-width:720px;padding:1em;">
    <div id="header">
      <p>Boilerplate Exo-Dev</p>
    </div>
"""

footer_mail_template = """
    <div id="footer">
      <br><br>
      A très vite &#128522;
      <br>
      <strong>L’équipe Exo-Dev</strong>
    </div>
    <br/>
    <p style="font-style: italic; text-align: center;">
        Ceci est un mail automatique, merci de ne pas y répondre.
    </p>
  </div>
</body>
</html>
"""

# ####################################################################################
#                         CORPS WITH TEMPLATE EXO-DEV
# ####################################################################################


corps_reset_password = """
<div id="content">
  <!--  RESET PASSWORD -->
  <h2 style="font-weight: normal;">Mot de passe <strong>oublié ?</strong></h2>
  <p>Nous avons reçu une demande de réinitialisation de mot de passe pour votre compte.</p>
  <br/>
  <p>
    Cliquez sur le bouton ci-dessous pour définir un nouveau mot de passe.<br>
    <em>Si vous n'êtes pas à l'origine de cette demande, vous pouvez ignorer ce message.</em>
  </p>
  <br/>
  <br/>
  <div style="text-align: center;">
    <!--[if mso]>
      <v:roundrect xmlns:v="urn:schemas-microsoft-com:vml" href="{0}"  xmlns:w="urn:schemas-microsoft-com:office:word" style="width: 500px; height: 50px; v-text-anchor: middle;" arcsize="100px" fillcolor="#11132A">
        <v:stroke opacity="0%"/>
        <w:anchorlock/>
        <center style="color: white; font-size: 1.25em; line-height: 1.25em; font-weight: bold;">
          Réinitialiser mon mot de passe
        </center>
      </v:roundrect>
    <![endif]-->
    <a href="{0}" target="_BLANK" style="text-decoration: none;">
      <span style="padding: 0.5em 1.5em; color: white; font-weight: bold; background-color: #11132A; border-radius: 100px; -webkit-text-size-adjust: none; mso-hide: all;">
        Réinitialiser mon mot de passe
      </span>
    </a>
    <p>
      &#x231A; Ce lien expirera dans {1}
    </p>
  </div>
  <p style="font-style: italic;">
    <br>
    Ou copiez le lien suivant dans votre navigateur :<br/>{0}
  </p>
<!-- END RESET PASSWORD -->
</div>
"""


corps_new_user = """
<div id="content">
  <!--  NEW USER ACCOUNT  -->
    <h2 style="font-weight: normal;">Bienvenue sur votre compte <strong>Boilerplate</strong></h2>
    <br/>
    <p>
      &#128073; Pour vous définir votre mot de passe et accéder à votre espace, il vous suffit de suivre le processus de première connexion en cliquant sur le bouton ci-dessous :<br>
      <em>Si vous n'êtes pas à l'origine de cette demande, vous pouvez ignorer ce message.</em>
    </p>
    <br><br>
    <div style="text-align: center;">
      <!--[if mso]>
        <v:roundrect xmlns:v="urn:schemas-microsoft-com:vml" href="{0}"  xmlns:w="urn:schemas-microsoft-com:office:word" style="width: 500px; height: 50px; v-text-anchor: middle;" arcsize="100px" fillcolor="#11132A">
          <v:stroke opacity="0%"/>
          <w:anchorlock/>
          <center style="color: white; font-size: 1.25em; line-height: 1.25em; font-weight: bold;">
            Première connexion
          </center>
        </v:roundrect>
      <![endif]-->
      <a href="{0}" target="_BLANK" style="text-decoration: none;">
        <span style="padding: 0.5em 1.5em; color: white; font-weight: bold; background-color: #11132A; border-radius: 100px; -webkit-text-size-adjust: none; mso-hide: all;">
          Première connexion
        </span>
      </a>
      <p>
        &#x231A; Ce lien expirera dans {1}
      </p>
    </div>
    <p style="font-style: italic;">
      <br>
      Ou copiez le lien suivant dans votre navigateur :<br/>{0}
    </p>
    <p>
      Si vous avez des questions, vous pouvez nous contacter à l’adresse suivante : <a href="mailto:{2}">{2}</a>.
    </p>
  <!-- END NEW USER ACCOUNT -->
</div>
"""


# ####################################################################################
#                       CORPS WITHOUT TEMPLATE EXO-DEV
# ####################################################################################
