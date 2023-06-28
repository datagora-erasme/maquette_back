
INSERT INTO base.authentications 
(email, password, role, status)
VALUES 
('x.thiermant@exo-dev.fr', 'meoK4zlCmwC5B9lvkNR1fWDYFwpNfLTV+SNZ3tV34cSZ6grjOUKbALkH2W+Q1HV9YNgXCk18tNX5I1ne1XfhxPpVN31F63BZERnonDsB32WMyuUDmcBofjTf+sUERpgV', 'SUPERADMIN', 'ACTIVE'),
('contact@exo-dev.fr', 'meoK4zlCmwC5B9lvkNR1fWDYFwpNfLTV+SNZ3tV34cSZ6grjOUKbALkH2W+Q1HV9YNgXCk18tNX5I1ne1XfhxPpVN31F63BZERnonDsB32WMyuUDmcBofjTf+sUERpgV', 'USER', 'ACTIVE'),
('c.raoux@exo-dev.fr', 'meoK4zlCmwC5B9lvkNR1fWDYFwpNfLTV+SNZ3tV34cSZ6grjOUKbALkH2W+Q1HV9YNgXCk18tNX5I1ne1XfhxPpVN31F63BZERnonDsB32WMyuUDmcBofjTf+sUERpgV', 'ADMIN', 'ACTIVE');


INSERT INTO base.users 
(firstname, lastname, phone, authentication_id)
VALUES 
('Xavier', 'Thiermant', '0654455523', 1),
('Contact', 'User', NULL, 2),
('Cindy', 'Raoux', NULL, 3);


INSERT INTO base.notifications
(title, type, content, link)
VALUES
('test info User', 'INFO', 'Notification de test User', NULL),
('test info Admin', 'INFO', 'Notification de test Admin', NULL),
('test warning User', 'WARNING', 'Notification de test User - vue', NULL),
('test Warning Admin', 'WARNING', 'Mesdames, messieurs, la volonté farouche de sortir notre pays de la crise nous assure à toutes et à tous les moyens d aller dans le sens de nos compatriotes les plus démunis', NULL),
('test info Admin', 'SUCCESS', 'Dossier du client John Doe a été validé !', NULL),
('test Alerte Admin', 'ALERT', 'Ah non attention, ce n est pas un simple sport car il y a de bonnes règles, de bonnes rules et cette officialité peut vraiment retarder ce qui devrait devenir...', NULL),
('test info Admin', 'SUCCESS', 'Haec igitur Epicuri non probo', NULL);


INSERT INTO base.notifications_users
(user_id, notification_id, is_viewed)
VALUES
(2, 1, true),
(1, 2, true),
(2, 3, false),
(1, 4, false),
(1, 5, false),
(1, 6, false),
(1, 7, false);