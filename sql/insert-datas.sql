
INSERT INTO base.authentications 
(email, password, role, status)
VALUES 
('x.thiermant@exo-dev.fr', 'meoK4zlCmwC5B9lvkNR1fWDYFwpNfLTV+SNZ3tV34cSZ6grjOUKbALkH2W+Q1HV9YNgXCk18tNX5I1ne1XfhxPpVN31F63BZERnonDsB32WMyuUDmcBofjTf+sUERpgV', 'SUPERADMIN', 'ACTIVE'),
('contact@exo-dev.fr', 'meoK4zlCmwC5B9lvkNR1fWDYFwpNfLTV+SNZ3tV34cSZ6grjOUKbALkH2W+Q1HV9YNgXCk18tNX5I1ne1XfhxPpVN31F63BZERnonDsB32WMyuUDmcBofjTf+sUERpgV', 'ADMIN', 'ACTIVE'),
('contact@exo-dev.fr', 'meoK4zlCmwC5B9lvkNR1fWDYFwpNfLTV+SNZ3tV34cSZ6grjOUKbALkH2W+Q1HV9YNgXCk18tNX5I1ne1XfhxPpVN31F63BZERnonDsB32WMyuUDmcBofjTf+sUERpgV', 'USER', 'ACTIVE');


INSERT INTO base.users 
(firstname, lastname, authentication_id)
VALUES 
('Xavier', 'Thiermant', 1),
('Sofiane', 'Hamlaoui', 2),
('Contact', 'User', 3);
