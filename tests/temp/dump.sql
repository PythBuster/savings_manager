--
-- PostgreSQL database dump
--

-- Dumped from database version 16.4 (Debian 16.4-1.pgdg120+1)
-- Dumped by pg_dump version 16.4 (Ubuntu 16.4-1.pgdg22.04+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: test_postgres
--

COPY public.alembic_version (version_num) FROM stdin;
ec5970020dee
\.


--
-- Data for Name: app_settings; Type: TABLE DATA; Schema: public; Owner: test_postgres
--

COPY public.app_settings (is_automated_saving_active, savings_amount, id, created_at, modified_at, is_active, note, overflow_moneybox_automated_savings_mode, send_reports_via_email, user_email_address) FROM stdin;
f	150	2	2024-09-18 13:11:49.661859+00	\N	t		FILL_UP_LIMITED_MONEYBOXES	f	pythbuster@gmail.com
\.


--
-- Data for Name: automated_savings_logs; Type: TABLE DATA; Schema: public; Owner: test_postgres
--

COPY public.automated_savings_logs (action_at, action, details, id, created_at, modified_at, is_active, note) FROM stdin;
\.


--
-- Data for Name: moneyboxes; Type: TABLE DATA; Schema: public; Owner: test_postgres
--

COPY public.moneyboxes (name, balance, savings_amount, savings_target, priority, id, created_at, modified_at, is_active, note) FROM stdin;
Overflow Moneybox	0	0	\N	0	2	2024-09-18 13:11:49.659017+00	\N	t	
Test Box 1	0	0	\N	1	3	2024-09-18 13:11:49.666557+00	\N	t	
\.


--
-- Data for Name: moneybox_name_histories; Type: TABLE DATA; Schema: public; Owner: test_postgres
--

COPY public.moneybox_name_histories (moneybox_id, name, id, created_at, modified_at, is_active, note) FROM stdin;
3	Test Box 1	1	2024-09-18 13:11:49.666557+00	\N	t	
\.


--
-- Data for Name: transactions; Type: TABLE DATA; Schema: public; Owner: test_postgres
--

COPY public.transactions (description, transaction_type, transaction_trigger, amount, balance, counterparty_moneybox_id, moneybox_id, id, created_at, modified_at, is_active, note) FROM stdin;
\.


--
-- Name: app_settings_id_seq; Type: SEQUENCE SET; Schema: public; Owner: test_postgres
--

SELECT pg_catalog.setval('public.app_settings_id_seq', 2, true);


--
-- Name: automated_savings_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: test_postgres
--

SELECT pg_catalog.setval('public.automated_savings_logs_id_seq', 1, false);


--
-- Name: moneybox_name_histories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: test_postgres
--

SELECT pg_catalog.setval('public.moneybox_name_histories_id_seq', 1, true);


--
-- Name: moneyboxes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: test_postgres
--

SELECT pg_catalog.setval('public.moneyboxes_id_seq', 3, true);


--
-- Name: transactions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: test_postgres
--

SELECT pg_catalog.setval('public.transactions_id_seq', 1, false);


--
-- PostgreSQL database dump complete
--

