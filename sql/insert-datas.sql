
INSERT INTO base.authentications 
(email, password, role, status)
VALUES 
('x.thiermant@exo-dev.fr', 'meoK4zlCmwC5B9lvkNR1fWDYFwpNfLTV+SNZ3tV34cSZ6grjOUKbALkH2W+Q1HV9YNgXCk18tNX5I1ne1XfhxPpVN31F63BZERnonDsB32WMyuUDmcBofjTf+sUERpgV', 'SUPERADMIN', 'ACTIVE'),
('contact@exo-dev.fr', 'meoK4zlCmwC5B9lvkNR1fWDYFwpNfLTV+SNZ3tV34cSZ6grjOUKbALkH2W+Q1HV9YNgXCk18tNX5I1ne1XfhxPpVN31F63BZERnonDsB32WMyuUDmcBofjTf+sUERpgV', 'USER', 'ACTIVE'),
('contact@exo-dev.fr', 'meoK4zlCmwC5B9lvkNR1fWDYFwpNfLTV+SNZ3tV34cSZ6grjOUKbALkH2W+Q1HV9YNgXCk18tNX5I1ne1XfhxPpVN31F63BZERnonDsB32WMyuUDmcBofjTf+sUERpgV', 'ADMIN', 'ACTIVE');


INSERT INTO base.users 
(firstname, lastname, phone, authentication_id)
VALUES 
('Xavier', 'Thiermant', '0654455523', 1),
('Contact', 'User', NULL, 2),
('Sofiane', 'Hamlaoui', NULL, 3);
