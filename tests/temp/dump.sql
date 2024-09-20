PGDMP      !    
            |           savings_manager    16.4 (Debian 16.4-1.pgdg120+1)     16.4 (Ubuntu 16.4-1.pgdg22.04+1) _    z           0    0    ENCODING    ENCODING        SET client_encoding = 'UTF8';
                      false            {           0    0 
   STDSTRINGS 
   STDSTRINGS     (   SET standard_conforming_strings = 'on';
                      false            |           0    0 
   SEARCHPATH 
   SEARCHPATH     8   SELECT pg_catalog.set_config('search_path', '', false);
                      false            }           1262    16384    savings_manager    DATABASE     z   CREATE DATABASE savings_manager WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'en_US.utf8';
    DROP DATABASE savings_manager;
                test_postgres    false            g           1247    17036 
   actiontype    TYPE     �   CREATE TYPE public.actiontype AS ENUM (
    'ACTIVATED_AUTOMATED_SAVING',
    'DEACTIVATED_AUTOMATED_SAVING',
    'APPLIED_AUTOMATED_SAVING',
    'CATCHED_UP_AUTOMATED_SAVING',
    'CHANGED_AUTOMATED_SAVINGS_AMOUNT'
);
    DROP TYPE public.actiontype;
       public          test_postgres    false            m           1247    17060 (   overflowmoneyboxautomatedsavingsmodetype    TYPE     �   CREATE TYPE public.overflowmoneyboxautomatedsavingsmodetype AS ENUM (
    'COLLECT',
    'ADD_TO_AUTOMATED_SAVINGS_AMOUNT',
    'FILL_UP_LIMITED_MONEYBOXES'
);
 ;   DROP TYPE public.overflowmoneyboxautomatedsavingsmodetype;
       public          test_postgres    false            ^           1247    16988    transactiontrigger    TYPE     W   CREATE TYPE public.transactiontrigger AS ENUM (
    'MANUALLY',
    'AUTOMATICALLY'
);
 %   DROP TYPE public.transactiontrigger;
       public          test_postgres    false            [           1247    16983    transactiontype    TYPE     Q   CREATE TYPE public.transactiontype AS ENUM (
    'DIRECT',
    'DISTRIBUTION'
);
 "   DROP TYPE public.transactiontype;
       public          test_postgres    false            �            1259    16385    alembic_version    TABLE     X   CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);
 #   DROP TABLE public.alembic_version;
       public         heap    test_postgres    false            �            1259    17020    app_settings    TABLE     �  CREATE TABLE public.app_settings (
    is_automated_saving_active boolean DEFAULT true NOT NULL,
    savings_amount integer DEFAULT 0 NOT NULL,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    modified_at timestamp with time zone,
    is_active boolean DEFAULT true NOT NULL,
    note character varying DEFAULT ''::character varying NOT NULL,
    overflow_moneybox_automated_savings_mode public.overflowmoneyboxautomatedsavingsmodetype DEFAULT 'COLLECT'::public.overflowmoneyboxautomatedsavingsmodetype NOT NULL,
    send_reports_via_email boolean DEFAULT false NOT NULL,
    user_email_address character varying,
    CONSTRAINT ck_app_settings_savings_amount_nonnegative CHECK ((savings_amount >= 0)),
    CONSTRAINT ck_app_settings_send_reports_via_email_requires_email_address CHECK ((((send_reports_via_email = true) AND (user_email_address IS NOT NULL)) OR (send_reports_via_email = false)))
);
     DROP TABLE public.app_settings;
       public         heap    test_postgres    false    877    877            ~           0    0 .   COLUMN app_settings.is_automated_saving_active    COMMENT     l   COMMENT ON COLUMN public.app_settings.is_automated_saving_active IS 'Tells if automated saving is active.';
          public          test_postgres    false    223                       0    0 "   COLUMN app_settings.savings_amount    COMMENT     �   COMMENT ON COLUMN public.app_settings.savings_amount IS 'The savings amount for the automated saving which will be distributed periodically to the moneyboxes, which have a (desired) savings amount > 0.';
          public          test_postgres    false    223            �           0    0    COLUMN app_settings.id    COMMENT     J   COMMENT ON COLUMN public.app_settings.id IS 'The primary ID of the row.';
          public          test_postgres    false    223            �           0    0    COLUMN app_settings.created_at    COMMENT     Q   COMMENT ON COLUMN public.app_settings.created_at IS 'The created utc datetime.';
          public          test_postgres    false    223            �           0    0    COLUMN app_settings.modified_at    COMMENT     S   COMMENT ON COLUMN public.app_settings.modified_at IS 'The modified utc datetime.';
          public          test_postgres    false    223            �           0    0    COLUMN app_settings.is_active    COMMENT     X   COMMENT ON COLUMN public.app_settings.is_active IS 'Flag to mark instance as deleted.';
          public          test_postgres    false    223            �           0    0    COLUMN app_settings.note    COMMENT     I   COMMENT ON COLUMN public.app_settings.note IS 'The note of this record';
          public          test_postgres    false    223            �           0    0 <   COLUMN app_settings.overflow_moneybox_automated_savings_mode    COMMENT     �   COMMENT ON COLUMN public.app_settings.overflow_moneybox_automated_savings_mode IS 'The mode for the overflow moneybox, which will have an influence on the automated savings process.';
          public          test_postgres    false    223            �           0    0 *   COLUMN app_settings.send_reports_via_email    COMMENT     |   COMMENT ON COLUMN public.app_settings.send_reports_via_email IS 'Tells if receiving reports via report_sender is desired.';
          public          test_postgres    false    223            �           0    0 &   COLUMN app_settings.user_email_address    COMMENT     u   COMMENT ON COLUMN public.app_settings.user_email_address IS 'Users email address. Will used for receiving reports.';
          public          test_postgres    false    223            �            1259    17019    app_settings_id_seq    SEQUENCE     �   CREATE SEQUENCE public.app_settings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 *   DROP SEQUENCE public.app_settings_id_seq;
       public          test_postgres    false    223            �           0    0    app_settings_id_seq    SEQUENCE OWNED BY     K   ALTER SEQUENCE public.app_settings_id_seq OWNED BY public.app_settings.id;
          public          test_postgres    false    222            �            1259    17048    automated_savings_logs    TABLE     �  CREATE TABLE public.automated_savings_logs (
    action_at timestamp with time zone NOT NULL,
    action public.actiontype NOT NULL,
    details json,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    modified_at timestamp with time zone,
    is_active boolean DEFAULT true NOT NULL,
    note character varying DEFAULT ''::character varying NOT NULL
);
 *   DROP TABLE public.automated_savings_logs;
       public         heap    test_postgres    false    871            �           0    0 '   COLUMN automated_savings_logs.action_at    COMMENT     `   COMMENT ON COLUMN public.automated_savings_logs.action_at IS 'The utc datetime of the action.';
          public          test_postgres    false    225            �           0    0 $   COLUMN automated_savings_logs.action    COMMENT     �   COMMENT ON COLUMN public.automated_savings_logs.action IS 'The action type within the automated savings and automated savings logs.';
          public          test_postgres    false    225            �           0    0 %   COLUMN automated_savings_logs.details    COMMENT     o   COMMENT ON COLUMN public.automated_savings_logs.details IS 'Metadata for the action, like app settings data.';
          public          test_postgres    false    225            �           0    0     COLUMN automated_savings_logs.id    COMMENT     T   COMMENT ON COLUMN public.automated_savings_logs.id IS 'The primary ID of the row.';
          public          test_postgres    false    225            �           0    0 (   COLUMN automated_savings_logs.created_at    COMMENT     [   COMMENT ON COLUMN public.automated_savings_logs.created_at IS 'The created utc datetime.';
          public          test_postgres    false    225            �           0    0 )   COLUMN automated_savings_logs.modified_at    COMMENT     ]   COMMENT ON COLUMN public.automated_savings_logs.modified_at IS 'The modified utc datetime.';
          public          test_postgres    false    225            �           0    0 '   COLUMN automated_savings_logs.is_active    COMMENT     b   COMMENT ON COLUMN public.automated_savings_logs.is_active IS 'Flag to mark instance as deleted.';
          public          test_postgres    false    225            �           0    0 "   COLUMN automated_savings_logs.note    COMMENT     S   COMMENT ON COLUMN public.automated_savings_logs.note IS 'The note of this record';
          public          test_postgres    false    225            �            1259    17047    automated_savings_logs_id_seq    SEQUENCE     �   CREATE SEQUENCE public.automated_savings_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 4   DROP SEQUENCE public.automated_savings_logs_id_seq;
       public          test_postgres    false    225            �           0    0    automated_savings_logs_id_seq    SEQUENCE OWNED BY     _   ALTER SEQUENCE public.automated_savings_logs_id_seq OWNED BY public.automated_savings_logs.id;
          public          test_postgres    false    224            �            1259    16966    moneybox_name_histories    TABLE     �  CREATE TABLE public.moneybox_name_histories (
    moneybox_id integer NOT NULL,
    name character varying NOT NULL,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    modified_at timestamp with time zone,
    is_active boolean DEFAULT true NOT NULL,
    note character varying DEFAULT ''::character varying NOT NULL,
    CONSTRAINT ck_moneybox_name_histories_name_no_leading_trailing_whitespace CHECK (((name)::text = TRIM(BOTH FROM name)))
);
 +   DROP TABLE public.moneybox_name_histories;
       public         heap    test_postgres    false            �           0    0 #   COLUMN moneybox_name_histories.name    COMMENT     Z   COMMENT ON COLUMN public.moneybox_name_histories.name IS 'The new name of the moneybox.';
          public          test_postgres    false    219            �           0    0 !   COLUMN moneybox_name_histories.id    COMMENT     U   COMMENT ON COLUMN public.moneybox_name_histories.id IS 'The primary ID of the row.';
          public          test_postgres    false    219            �           0    0 )   COLUMN moneybox_name_histories.created_at    COMMENT     \   COMMENT ON COLUMN public.moneybox_name_histories.created_at IS 'The created utc datetime.';
          public          test_postgres    false    219            �           0    0 *   COLUMN moneybox_name_histories.modified_at    COMMENT     ^   COMMENT ON COLUMN public.moneybox_name_histories.modified_at IS 'The modified utc datetime.';
          public          test_postgres    false    219            �           0    0 (   COLUMN moneybox_name_histories.is_active    COMMENT     c   COMMENT ON COLUMN public.moneybox_name_histories.is_active IS 'Flag to mark instance as deleted.';
          public          test_postgres    false    219            �           0    0 #   COLUMN moneybox_name_histories.note    COMMENT     T   COMMENT ON COLUMN public.moneybox_name_histories.note IS 'The note of this record';
          public          test_postgres    false    219            �            1259    16965    moneybox_name_histories_id_seq    SEQUENCE     �   CREATE SEQUENCE public.moneybox_name_histories_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 5   DROP SEQUENCE public.moneybox_name_histories_id_seq;
       public          test_postgres    false    219            �           0    0    moneybox_name_histories_id_seq    SEQUENCE OWNED BY     a   ALTER SEQUENCE public.moneybox_name_histories_id_seq OWNED BY public.moneybox_name_histories.id;
          public          test_postgres    false    218            �            1259    16943 
   moneyboxes    TABLE       CREATE TABLE public.moneyboxes (
    name character varying NOT NULL,
    balance integer DEFAULT 0 NOT NULL,
    savings_amount integer DEFAULT 0 NOT NULL,
    savings_target integer,
    priority integer,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    modified_at timestamp with time zone,
    is_active boolean DEFAULT true NOT NULL,
    note character varying DEFAULT ''::character varying NOT NULL,
    CONSTRAINT ck_moneyboxes_ck_moneyboxes_balance_nonnegative CHECK ((balance >= 0)),
    CONSTRAINT ck_moneyboxes_ck_moneyboxes_is_active_balance CHECK ((NOT ((is_active = false) AND (balance <> 0)))),
    CONSTRAINT ck_moneyboxes_ck_moneyboxes_name_nonempty CHECK ((char_length(TRIM(BOTH FROM name)) > 0)),
    CONSTRAINT ck_moneyboxes_ck_moneyboxes_priority_if_inactive CHECK (((is_active = true) OR (priority IS NULL))),
    CONSTRAINT ck_moneyboxes_ck_moneyboxes_priority_nonnegative CHECK ((priority >= 0)),
    CONSTRAINT ck_moneyboxes_ck_moneyboxes_savings_amount_nonnegative CHECK ((savings_amount >= 0)),
    CONSTRAINT ck_moneyboxes_ck_moneyboxes_savings_target_nonnegative CHECK (((savings_target IS NULL) OR (savings_target >= 0))),
    CONSTRAINT ck_moneyboxes_name_no_leading_trailing_whitespace CHECK (((name)::text = TRIM(BOTH FROM name)))
);
    DROP TABLE public.moneyboxes;
       public         heap    test_postgres    false            �           0    0    COLUMN moneyboxes.name    COMMENT     I   COMMENT ON COLUMN public.moneyboxes.name IS 'The name of the moneybox.';
          public          test_postgres    false    217            �           0    0    COLUMN moneyboxes.balance    COMMENT     W   COMMENT ON COLUMN public.moneyboxes.balance IS 'The current balance of the moneybox.';
          public          test_postgres    false    217            �           0    0     COLUMN moneyboxes.savings_amount    COMMENT     e   COMMENT ON COLUMN public.moneyboxes.savings_amount IS 'The current savings amount of the moneybox.';
          public          test_postgres    false    217            �           0    0     COLUMN moneyboxes.savings_target    COMMENT     �   COMMENT ON COLUMN public.moneyboxes.savings_target IS 'The current savings target. Is relevant for the automated distributed saving progress.';
          public          test_postgres    false    217            �           0    0    COLUMN moneyboxes.priority    COMMENT     �   COMMENT ON COLUMN public.moneyboxes.priority IS 'The current priority of the moneybox. There is only one moneybox with a priority of Null (will be the marker for the overflow moneybox. And only disables moneyboxes cant have e NULL value as priority.';
          public          test_postgres    false    217            �           0    0    COLUMN moneyboxes.id    COMMENT     H   COMMENT ON COLUMN public.moneyboxes.id IS 'The primary ID of the row.';
          public          test_postgres    false    217            �           0    0    COLUMN moneyboxes.created_at    COMMENT     O   COMMENT ON COLUMN public.moneyboxes.created_at IS 'The created utc datetime.';
          public          test_postgres    false    217            �           0    0    COLUMN moneyboxes.modified_at    COMMENT     Q   COMMENT ON COLUMN public.moneyboxes.modified_at IS 'The modified utc datetime.';
          public          test_postgres    false    217            �           0    0    COLUMN moneyboxes.is_active    COMMENT     V   COMMENT ON COLUMN public.moneyboxes.is_active IS 'Flag to mark instance as deleted.';
          public          test_postgres    false    217            �           0    0    COLUMN moneyboxes.note    COMMENT     G   COMMENT ON COLUMN public.moneyboxes.note IS 'The note of this record';
          public          test_postgres    false    217            �            1259    16942    moneyboxes_id_seq    SEQUENCE     �   CREATE SEQUENCE public.moneyboxes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 (   DROP SEQUENCE public.moneyboxes_id_seq;
       public          test_postgres    false    217            �           0    0    moneyboxes_id_seq    SEQUENCE OWNED BY     G   ALTER SEQUENCE public.moneyboxes_id_seq OWNED BY public.moneyboxes.id;
          public          test_postgres    false    216            �            1259    16994    transactions    TABLE     �  CREATE TABLE public.transactions (
    description character varying DEFAULT ''::character varying NOT NULL,
    transaction_type public.transactiontype NOT NULL,
    transaction_trigger public.transactiontrigger NOT NULL,
    amount integer NOT NULL,
    balance integer NOT NULL,
    counterparty_moneybox_id integer,
    moneybox_id integer NOT NULL,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    modified_at timestamp with time zone,
    is_active boolean DEFAULT true NOT NULL,
    note character varying DEFAULT ''::character varying NOT NULL,
    CONSTRAINT ck_transactions_ck_transactions_balance_nonnegative CHECK ((balance >= 0))
);
     DROP TABLE public.transactions;
       public         heap    test_postgres    false    859    862            �           0    0    COLUMN transactions.description    COMMENT     c   COMMENT ON COLUMN public.transactions.description IS 'The description of the transaction action.';
          public          test_postgres    false    221            �           0    0 $   COLUMN transactions.transaction_type    COMMENT     �   COMMENT ON COLUMN public.transactions.transaction_type IS 'The type of the transaction. Possible values: direct or distribution.';
          public          test_postgres    false    221            �           0    0 '   COLUMN transactions.transaction_trigger    COMMENT     �   COMMENT ON COLUMN public.transactions.transaction_trigger IS 'The transaction trigger type, possible values: manually, automatically. Says, if balance was deposit or withdrawn manually or automatically.';
          public          test_postgres    false    221            �           0    0    COLUMN transactions.amount    COMMENT     �   COMMENT ON COLUMN public.transactions.amount IS 'The current amount of the transaction. Can be negative, negative = withdraw, positive = deposit.';
          public          test_postgres    false    221            �           0    0    COLUMN transactions.balance    COMMENT     p   COMMENT ON COLUMN public.transactions.balance IS 'The balance of the moneybox at the time of the transaction.';
          public          test_postgres    false    221            �           0    0 ,   COLUMN transactions.counterparty_moneybox_id    COMMENT     �   COMMENT ON COLUMN public.transactions.counterparty_moneybox_id IS 'Transaction is a transfer between moneybox_id and counterparty_moneybox_id, if set.';
          public          test_postgres    false    221            �           0    0    COLUMN transactions.id    COMMENT     J   COMMENT ON COLUMN public.transactions.id IS 'The primary ID of the row.';
          public          test_postgres    false    221            �           0    0    COLUMN transactions.created_at    COMMENT     Q   COMMENT ON COLUMN public.transactions.created_at IS 'The created utc datetime.';
          public          test_postgres    false    221            �           0    0    COLUMN transactions.modified_at    COMMENT     S   COMMENT ON COLUMN public.transactions.modified_at IS 'The modified utc datetime.';
          public          test_postgres    false    221            �           0    0    COLUMN transactions.is_active    COMMENT     X   COMMENT ON COLUMN public.transactions.is_active IS 'Flag to mark instance as deleted.';
          public          test_postgres    false    221            �           0    0    COLUMN transactions.note    COMMENT     I   COMMENT ON COLUMN public.transactions.note IS 'The note of this record';
          public          test_postgres    false    221            �            1259    16993    transactions_id_seq    SEQUENCE     �   CREATE SEQUENCE public.transactions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 *   DROP SEQUENCE public.transactions_id_seq;
       public          test_postgres    false    221            �           0    0    transactions_id_seq    SEQUENCE OWNED BY     K   ALTER SEQUENCE public.transactions_id_seq OWNED BY public.transactions.id;
          public          test_postgres    false    220            �           2604    17026    app_settings id    DEFAULT     r   ALTER TABLE ONLY public.app_settings ALTER COLUMN id SET DEFAULT nextval('public.app_settings_id_seq'::regclass);
 >   ALTER TABLE public.app_settings ALTER COLUMN id DROP DEFAULT;
       public          test_postgres    false    222    223    223            �           2604    17051    automated_savings_logs id    DEFAULT     �   ALTER TABLE ONLY public.automated_savings_logs ALTER COLUMN id SET DEFAULT nextval('public.automated_savings_logs_id_seq'::regclass);
 H   ALTER TABLE public.automated_savings_logs ALTER COLUMN id DROP DEFAULT;
       public          test_postgres    false    225    224    225            �           2604    16969    moneybox_name_histories id    DEFAULT     �   ALTER TABLE ONLY public.moneybox_name_histories ALTER COLUMN id SET DEFAULT nextval('public.moneybox_name_histories_id_seq'::regclass);
 I   ALTER TABLE public.moneybox_name_histories ALTER COLUMN id DROP DEFAULT;
       public          test_postgres    false    218    219    219            �           2604    16948    moneyboxes id    DEFAULT     n   ALTER TABLE ONLY public.moneyboxes ALTER COLUMN id SET DEFAULT nextval('public.moneyboxes_id_seq'::regclass);
 <   ALTER TABLE public.moneyboxes ALTER COLUMN id DROP DEFAULT;
       public          test_postgres    false    217    216    217            �           2604    16998    transactions id    DEFAULT     r   ALTER TABLE ONLY public.transactions ALTER COLUMN id SET DEFAULT nextval('public.transactions_id_seq'::regclass);
 >   ALTER TABLE public.transactions ALTER COLUMN id DROP DEFAULT;
       public          test_postgres    false    220    221    221            m          0    16385    alembic_version 
   TABLE DATA           6   COPY public.alembic_version (version_num) FROM stdin;
    public          test_postgres    false    215            u          0    17020    app_settings 
   TABLE DATA           �   COPY public.app_settings (is_automated_saving_active, savings_amount, id, created_at, modified_at, is_active, note, overflow_moneybox_automated_savings_mode, send_reports_via_email, user_email_address) FROM stdin;
    public          test_postgres    false    223            w          0    17048    automated_savings_logs 
   TABLE DATA           z   COPY public.automated_savings_logs (action_at, action, details, id, created_at, modified_at, is_active, note) FROM stdin;
    public          test_postgres    false    225            q          0    16966    moneybox_name_histories 
   TABLE DATA           r   COPY public.moneybox_name_histories (moneybox_id, name, id, created_at, modified_at, is_active, note) FROM stdin;
    public          test_postgres    false    219            o          0    16943 
   moneyboxes 
   TABLE DATA           �   COPY public.moneyboxes (name, balance, savings_amount, savings_target, priority, id, created_at, modified_at, is_active, note) FROM stdin;
    public          test_postgres    false    217            s          0    16994    transactions 
   TABLE DATA           �   COPY public.transactions (description, transaction_type, transaction_trigger, amount, balance, counterparty_moneybox_id, moneybox_id, id, created_at, modified_at, is_active, note) FROM stdin;
    public          test_postgres    false    221            �           0    0    app_settings_id_seq    SEQUENCE SET     A   SELECT pg_catalog.setval('public.app_settings_id_seq', 2, true);
          public          test_postgres    false    222            �           0    0    automated_savings_logs_id_seq    SEQUENCE SET     L   SELECT pg_catalog.setval('public.automated_savings_logs_id_seq', 1, false);
          public          test_postgres    false    224            �           0    0    moneybox_name_histories_id_seq    SEQUENCE SET     L   SELECT pg_catalog.setval('public.moneybox_name_histories_id_seq', 1, true);
          public          test_postgres    false    218            �           0    0    moneyboxes_id_seq    SEQUENCE SET     ?   SELECT pg_catalog.setval('public.moneyboxes_id_seq', 3, true);
          public          test_postgres    false    216            �           0    0    transactions_id_seq    SEQUENCE SET     B   SELECT pg_catalog.setval('public.transactions_id_seq', 1, false);
          public          test_postgres    false    220            �           2606    16389 #   alembic_version alembic_version_pkc 
   CONSTRAINT     j   ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);
 M   ALTER TABLE ONLY public.alembic_version DROP CONSTRAINT alembic_version_pkc;
       public            test_postgres    false    215            �           2606    17034    app_settings pk_app_settings 
   CONSTRAINT     Z   ALTER TABLE ONLY public.app_settings
    ADD CONSTRAINT pk_app_settings PRIMARY KEY (id);
 F   ALTER TABLE ONLY public.app_settings DROP CONSTRAINT pk_app_settings;
       public            test_postgres    false    223            �           2606    17058 0   automated_savings_logs pk_automated_savings_logs 
   CONSTRAINT     n   ALTER TABLE ONLY public.automated_savings_logs
    ADD CONSTRAINT pk_automated_savings_logs PRIMARY KEY (id);
 Z   ALTER TABLE ONLY public.automated_savings_logs DROP CONSTRAINT pk_automated_savings_logs;
       public            test_postgres    false    225            �           2606    16976 2   moneybox_name_histories pk_moneybox_name_histories 
   CONSTRAINT     p   ALTER TABLE ONLY public.moneybox_name_histories
    ADD CONSTRAINT pk_moneybox_name_histories PRIMARY KEY (id);
 \   ALTER TABLE ONLY public.moneybox_name_histories DROP CONSTRAINT pk_moneybox_name_histories;
       public            test_postgres    false    219            �           2606    16962    moneyboxes pk_moneyboxes 
   CONSTRAINT     V   ALTER TABLE ONLY public.moneyboxes
    ADD CONSTRAINT pk_moneyboxes PRIMARY KEY (id);
 B   ALTER TABLE ONLY public.moneyboxes DROP CONSTRAINT pk_moneyboxes;
       public            test_postgres    false    217            �           2606    17006    transactions pk_transactions 
   CONSTRAINT     Z   ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT pk_transactions PRIMARY KEY (id);
 F   ALTER TABLE ONLY public.transactions DROP CONSTRAINT pk_transactions;
       public            test_postgres    false    221            �           1259    16963 !   idx_unique_moneyboxes_name_active    INDEX     x   CREATE UNIQUE INDEX idx_unique_moneyboxes_name_active ON public.moneyboxes USING btree (name) WHERE (is_active = true);
 5   DROP INDEX public.idx_unique_moneyboxes_name_active;
       public            test_postgres    false    217    217            �           1259    16964 %   idx_unique_moneyboxes_priority_active    INDEX     �   CREATE UNIQUE INDEX idx_unique_moneyboxes_priority_active ON public.moneyboxes USING btree (priority) WHERE (is_active = true);
 9   DROP INDEX public.idx_unique_moneyboxes_priority_active;
       public            test_postgres    false    217    217            �           2606    16977 I   moneybox_name_histories fk_moneybox_name_histories_moneybox_id_moneyboxes    FK CONSTRAINT     �   ALTER TABLE ONLY public.moneybox_name_histories
    ADD CONSTRAINT fk_moneybox_name_histories_moneybox_id_moneyboxes FOREIGN KEY (moneybox_id) REFERENCES public.moneyboxes(id) ON DELETE CASCADE;
 s   ALTER TABLE ONLY public.moneybox_name_histories DROP CONSTRAINT fk_moneybox_name_histories_moneybox_id_moneyboxes;
       public          test_postgres    false    217    219    3283            �           2606    17007 3   transactions fk_transactions_moneybox_id_moneyboxes    FK CONSTRAINT     �   ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT fk_transactions_moneybox_id_moneyboxes FOREIGN KEY (moneybox_id) REFERENCES public.moneyboxes(id) ON DELETE CASCADE;
 ]   ALTER TABLE ONLY public.transactions DROP CONSTRAINT fk_transactions_moneybox_id_moneyboxes;
       public          test_postgres    false    221    217    3283            m      x�KM6�47002HIM����� ,�      u   k   x�K�445�4�4202�5��52P0��26�22�30�4���60����,��t��������qu����s�t�p�L�,�,�H*-.I-rH�M���K������� e�j      w      x������ � �      q   ?   x�3�I-.QpʯP0�4�4202�5��52P0��26�22�30662�60����,������ S�
      o   _   x��/K-J��/W���K�Lʯ�4 �? a�id`d�k`�kd�``aelled�g`dff`�m VT���Z\���_�`�i�i�]����!Bc� ��x      s      x������ � �     