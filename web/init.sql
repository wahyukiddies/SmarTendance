-- smartendance_db
-- MySQL latest version

-- 1. ADD CLASS

INSERT INTO `class` (`class_id`, `class_study_program`, `class_major`, `class_description`) VALUES
('TI-1A', 'TI', 'TIK', NULL),
('TI-1B', 'TI', 'TIK', NULL),
('TI-2A', 'TI', 'TIK', NULL),
('TI-2B', 'TI', 'TIK', NULL),
('TI-3A', 'TI', 'TIK', NULL),
('TI-3B', 'TI', 'TIK', NULL),
('TI-4A', 'TI', 'TIK', NULL),
('TI-4B', 'TI', 'TIK', NULL),
('TI-5A', 'TI', 'TIK', NULL),
('TI-5B', 'TI', 'TIK', NULL),
('TI-6A', 'TI', 'TIK', NULL),
('TI-6B', 'TI', 'TIK', NULL),
('TI-7A', 'TI', 'TIK', NULL),
('TI-7B', 'TI', 'TIK', NULL),
('TI-8A', 'TI', 'TIK', NULL),
('TI-8B', 'TI', 'TIK', NULL),
('TMD-1A', 'TMD', 'TIK', NULL),
('TMD-1B', 'TMD', 'TIK', NULL),
('TMD-2A', 'TMD', 'TIK', NULL),
('TMD-2B', 'TMD', 'TIK', NULL),
('TMD-3A', 'TMD', 'TIK', NULL),
('TMD-3B', 'TMD', 'TIK', NULL),
('TMD-4A', 'TMD', 'TIK', NULL),
('TMD-4B', 'TMD', 'TIK', NULL),
('TMD-5A', 'TMD', 'TIK', NULL),
('TMD-5B', 'TMD', 'TIK', NULL),
('TMD-6A', 'TMD', 'TIK', NULL),
('TMD-6B', 'TMD', 'TIK', NULL),
('TMD-7A', 'TMD', 'TIK', NULL),
('TMD-7B', 'TMD', 'TIK', NULL),
('TMD-8A', 'TMD', 'TIK', NULL),
('TMD-8B', 'TMD', 'TIK', NULL),
('TMJ-1A', 'TMJ', 'TIK', NULL),
('TMJ-1B', 'TMJ', 'TIK', NULL),
('TMJ-2A', 'TMJ', 'TIK', NULL),
('TMJ-2B', 'TMJ', 'TIK', NULL),
('TMJ-3A', 'TMJ', 'TIK', NULL),
('TMJ-3B', 'TMJ', 'TIK', NULL),
('TMJ-4A', 'TMJ', 'TIK', NULL),
('TMJ-4B', 'TMJ', 'TIK', NULL),
('TMJ-5A', 'TMJ', 'TIK', NULL),
('TMJ-5B', 'TMJ', 'TIK', NULL),
('TMJ-6A', 'TMJ', 'TIK', NULL),
('TMJ-6B', 'TMJ', 'TIK', NULL),
('TMJ-7A', 'TMJ', 'TIK', NULL),
('TMJ-7B', 'TMJ', 'TIK', NULL),
('TMJ-8A', 'TMJ', 'TIK', NULL),
('TMJ-8B', 'TMJ', 'TIK', NULL),
('TKJ-1A', 'TKJ', 'TIK', NULL),
('TKJ-1B', 'TKJ', 'TIK', NULL),
('TKJ-2A', 'TKJ', 'TIK', NULL),
('TKJ-2B', 'TKJ', 'TIK', NULL);

-- 2. ADD ROOM

INSERT INTO `room` (`room_id`, `room_building`, `room_description`) VALUES
('AA204', 'AA', NULL),
('AA205', 'AA', NULL),
('AA301', 'AA', NULL),
('AA302', 'AA', NULL),
('AA303', 'AA', NULL),
('AA304', 'AA', NULL),
('AA305', 'AA', NULL),
('GSG202', 'GSG', NULL),
('GSG203', 'GSG', NULL),
('GSG206', 'GSG', NULL),
('GSG207', 'GSG', NULL),
('GSG208', 'GSG', NULL),
('GSG209', 'GSG', NULL),
('GSG210', 'GSG', NULL),
('GSG211', 'GSG', NULL),
('GSG212', 'GSG', NULL);

-- 3. ADD USER

INSERT INTO `user` (`user_id`, `user_role`, `user_fullname`, `user_password_hash`, `user_rfid`, `user_email_address`, `user_home_address`, `lecturer_major`, `student_class`) VALUES
('1234567890', 'ADMIN', 'Administrator', '$argon2id$v=19$m=65536,t=3,p=4$/NVHzuosbajWfAcrWiv+kg$afqhI0LRGJOGnL7/wJ2RzGWbz/3F/8+mUieQaCvbzwE', NULL, 'admin@tik.pnj.ac.id', NULL, NULL, NULL),
('197509152003122003', 'LECTURER', 'Maria Agustin', '$argon2id$v=19$m=65536,t=3,p=4$ssO7Dv0WIm3/Y5RNFsRdPg$H5SDId/KdDEnccPbojyW67HbMLrk1vbLlGDtFDzUYbQ', '$argon2id$v=19$m=65536,t=3,p=4$D9TTejpOGLHveQKtRtcPyg$9kwGOgacBeJJSDO6wZZWOCSnZuQbuTKYK7yyJfxIjDA', 'maria.agustin@tik.pnj.ac.id', NULL, 'TIK', NULL),
('197910062003122001', 'LECTURER', 'Prihatin Oktivasari', '$argon2id$v=19$m=65536,t=3,p=4$mCP2f/ZXJNu7Qkzvux/zKw$3sE/H6SNKCfZTeegg48Oqpg1+vZp8HrxwQEz8JJ7NEc', NULL, 'prihatin.oktivasari@tik.pnj.ac.id', NULL, 'TIK', NULL),
('198112012015041001', 'LECTURER', 'Defiana Arnaldy', '$argon2id$v=19$m=65536,t=3,p=4$2PUg2Kr/10shESpi+hTHQw$5RrxFO+m+2H04AqthOvXwFuKbV5RKrxMlv2nQQzYo6w', NULL, 'defiana.arnaldy@tik.pnj.ac.id', NULL, 'TIK', NULL),
('198501292010121003', 'LECTURER', 'Ariawan Andi Suhandana', '$argon2id$v=19$m=65536,t=3,p=4$1etgUc0HcAtgsMjuUysZqg$94Y1tSgl4WTBUcmGCK6/E5jVNVQGmTeRkTcmGtMl3zg', NULL, 'ariawan.andi.suhandana@tik.pnj.ac.id', NULL, 'TIK', NULL),
('198605222023212032', 'LECTURER', 'Susana Dwi Yulianti', '$argon2id$v=19$m=65536,t=3,p=4$on3Mb/aNBuBejfi5N4fZ4A$H2Hmf1HyeBDS2TRiXYGctk2/ZvKkQfkKwi7D9FDyckM', NULL, 'susana.dwiyulianti@tik.pnj.ac.id', NULL, 'TIK', NULL),
('198910112018032002', 'LECTURER', 'Ayu Rosyida Zain', '$argon2id$v=19$m=65536,t=3,p=4$mEq/jVbk/vComXCMaSL9+w$/o4O0/qJaa3kXAaQcGb79ujoNhS9as6xAnItx8s3hFs', NULL, 'ayu.rosyidazain@tik.pnj.ac.id', NULL, 'TIK', NULL),
('199109262019031012', 'LECTURER', 'Asep Kurniawan', '$argon2id$v=19$m=65536,t=3,p=4$m4FRK+CV3rAiuQBzMedoQQ$S/hlkIwFnUJLhZfwzCeY/u5to+8T5gkiXWJkQW4TNYI', NULL, 'asep.kurniawan@tik.pnj.ac.id', NULL, 'TIK', NULL),
('199206052022032008', 'LECTURER', 'Ratna Widya Iswara', '$argon2id$v=19$m=65536,t=3,p=4$AiccjdDQaJ45DBwu3qPBpw$XCKv3pm67q89vAziRRQN6WoXIjW999vTqrRz4vxtt6Q', NULL, 'ratna.widya.iswara@tik.pnj.ac.id', NULL, 'TIK', NULL),
('199408202022031009', 'LECTURER', 'Iik Muhamad Malik Matin', '$argon2id$v=19$m=65536,t=3,p=4$y78B+oyVIl9QAYXCOOwp/A$AC/xH9xuKb2G4O896gEM1lLU8/peF007FzYbsmEcqfc', NULL, 'iik.muhamad.malik.matin@tik.pnj.ac.id', NULL, 'TIK', NULL),
('2207421031', 'STUDENT', 'Muhammad Khairu Mufid', '$argon2id$v=19$m=65536,t=3,p=4$M4/Uhl73xK8tluGqpJE0UQ$hcSLDrk6m4rTE4Sqijcz4i3Ln7gDnWg/vqZzfNhHozc', "a75a4662", 'muhammad.khairu.mufid.tik22@mhsw.pnj.ac.id', 'None', NULL, 'TMJ-4B'),
('2207421032', 'STUDENT', 'Kevin Alonzo Manuel Bakara', '$argon2id$v=19$m=65536,t=3,p=4$xI/30BK3vcUWqEjTxxYPlA$AAUlYoIL1WAP/2PTgTnVDinb7S+RZFRMcy6nt1RUmqI', "23382510", 'kevin.alonzo.manuel.bakara.tik22@mhsw.pnj.ac.id', NULL, NULL, 'TMJ-4B'),
('2207421033', 'STUDENT', 'Devina Anggraini', '$argon2id$v=19$m=65536,t=3,p=4$MeUyzX+cmpu29ahcSd13uw$gKBRAWDLVCrvqNs/4BfQmXgjHA8TThE3UIpcHR90f2g', NULL, 'devina.anggraini.tik22@mhsw.pnj.ac.id', NULL, NULL, 'TMJ-4B'),
('2207421034', 'STUDENT', 'Alif Rendina Pamungkas', '$argon2id$v=19$m=65536,t=3,p=4$sUvXOSCu0z6CaHJcb1eo5w$gduQsF5APel878L+DDTfKsD/YsE/whgbDDZz8uN7LIg', NULL, 'alif.rendina.pamungkas.tik22@mhsw.pnj.ac.id', NULL, NULL, 'TMJ-4B'),
('2207421035', 'STUDENT', 'Ibrahim Alvaro', '$argon2id$v=19$m=65536,t=3,p=4$sIpl4fXTMLxcAwOolJgBPQ$l/xChySkOjL3x569fqqVcFMNwKWafNJ3QDRskVKBGX0', NULL, 'ibrahim.alvaro.tik22@mhsw.pnj.ac.id', NULL, NULL, 'TMJ-4B'),
('2207421047', 'STUDENT', 'Abdurrahman Ammar Ihsan', '$argon2id$v=19$m=65536,t=3,p=4$EwB4tzes72AfYndnT8uYLA$2BcT1aCeZ62G3h1OCiNh19Ku1Pc5OYpN2VhsV4C+lVU', NULL, 'abdurrahman.ammar.ihsan.tik22@mhsw.pnj.ac.id', NULL, NULL, 'TMJ-4B'),
('2207421048', 'STUDENT', 'Wahyu Priambodo', '$argon2id$v=19$m=65536,t=3,p=4$Loo/a50SSz2jKbxXwSCy/g$KKGaABgdeRe0habVBr3GHrhyzxs49J3U3uDfBEBFArw', "41032e256f80", 'wahyu.priambodo.tik22@mhsw.pnj.ac.id', NULL, NULL, 'TMJ-4B'),
('2207421049', 'STUDENT', 'Salsabila Aulia', '$argon2id$v=19$m=65536,t=3,p=4$IKqSDcXBACgQHPBsQb8RZQ$iHAJlO0nDmmlquGI2Xh9Jipngz3LK0IbURBcAU3gYbU', NULL, 'salsabila.aulia.tik22@mhsw.pnj.ac.id', NULL, NULL, 'TMJ-4B'),
('2207421056', 'STUDENT', 'Muhammad Brian Azura Nixon', '$argon2id$v=19$m=65536,t=3,p=4$NijZ400iDOzAFcrthn543Q$Fd7o94RdGjuHyHL5PK/hV8Z7Ydm6T5SSQ5IvxnX/ATA', NULL, 'muhammad.brian.azura.nixon.tik22@mhsw.pnj.ac.id', NULL, NULL, 'TMJ-4B'),
('2207421057', 'STUDENT', 'Shaquille Arriza Hidayat', '$argon2id$v=19$m=65536,t=3,p=4$x9gutpgd4xseDPAAkGruWg$rIQbuIN7dy81rx9l+xNDM10Fi9K1MBlmoH7x+lw6HWw', NULL, 'shaquille.arriza.hidayat.tik22@mhsw.pnj.ac.id', NULL, NULL, 'TMJ-4B'),
('2207421059', 'STUDENT', 'Cornelius Yuli Rosdianto', '$argon2id$v=19$m=65536,t=3,p=4$OyvSt33WArCGKAdKxlrtfA$UrMxvFOJoUALfydCnYXLKhaYa7rdQYhGBv1UGFUH0hI', NULL, 'cornelius.yuli.rosdianto.tik22@mhsw.pnj.ac.id', NULL, NULL, 'TMJ-4B');

-- 4. ADD COURSE

INSERT INTO `course` (`course_id`, `course_name`, `course_sks`, `at_semester`, `day`, `time_start`, `time_end`, `course_description`, `lecturer_nip`, `class_id`, `room_id`) VALUES
('TMJ405', 'Jaringan Server', 2, 4, 'Friday', '10:50:00', '16:05:00', NULL, '199109262019031012', 'TMJ-4B', 'AA204'),
('TMJ408', 'Pemrograman Perangkat Jaringan', 2, 4, 'Thursday', '12:30:00', '16:05:00', NULL, '198501292010121003', 'TMJ-4B', 'AA304'),
('TMJ407', 'Keamanan Sistem Informasi', 2, 4, 'Thursday', '07:30:00', '10:50:00', NULL, '198112012015041001', 'TMJ-4B', 'AA205'),
('TMJ409', 'Kriptografi', 2, 4, 'Tuesday', '07:30:00', '10:50:00', NULL, '199408202022031009', 'TMJ-4B', 'GSG211'),
('TMJ404', 'Metodologi Penelitian', 2, 4, 'Monday', '13:20:00', '16:55:00', NULL, '198910112018032002', 'TMJ-4B', 'GSG211');
