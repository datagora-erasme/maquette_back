
INSERT INTO base.authentications 
(email, password, role, status)
VALUES 
('contact@exo-dev.fr', 'meoK4zlCmwC5B9lvkNR1fWDYFwpNfLTV+SNZ3tV34cSZ6grjOUKbALkH2W+Q1HV9YNgXCk18tNX5I1ne1XfhxPpVN31F63BZERnonDsB32WMyuUDmcBofjTf+sUERpgV', 'SUPERADMIN', 'ACTIVE'),
('admin@exo-dev.fr', 'meoK4zlCmwC5B9lvkNR1fWDYFwpNfLTV+SNZ3tV34cSZ6grjOUKbALkH2W+Q1HV9YNgXCk18tNX5I1ne1XfhxPpVN31F63BZERnonDsB32WMyuUDmcBofjTf+sUERpgV', 'ADMIN', 'ACTIVE'),
('user@exo-dev.fr', 'meoK4zlCmwC5B9lvkNR1fWDYFwpNfLTV+SNZ3tV34cSZ6grjOUKbALkH2W+Q1HV9YNgXCk18tNX5I1ne1XfhxPpVN31F63BZERnonDsB32WMyuUDmcBofjTf+sUERpgV', 'USER', 'ACTIVE');


INSERT INTO base.users 
(firstname, lastname, authentication_id)
VALUES 
('Contact', 'Exo', 1),
('Admin', 'Exo', 2),
('User', 'Exo', 3);
