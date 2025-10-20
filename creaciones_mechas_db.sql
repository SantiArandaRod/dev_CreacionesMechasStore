--
-- PostgreSQL database dump
--

\restrict ZrGjidFvxPBSYz1dc83iUSX57D2fd9uS4SWHLlhYC6uX9KKeOyy6z1Ne5KxOfnI

-- Dumped from database version 17.6 (Debian 17.6-1.pgdg12+1)
-- Dumped by pg_dump version 17.6 (Debian 17.6-1.pgdg12+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: categoria; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.categoria (
    id_categoria integer NOT NULL,
    codigo character varying(10),
    tipo character varying(50) NOT NULL
);


ALTER TABLE public.categoria OWNER TO postgres;

--
-- Name: categoria_id_categoria_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.categoria_id_categoria_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.categoria_id_categoria_seq OWNER TO postgres;

--
-- Name: categoria_id_categoria_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.categoria_id_categoria_seq OWNED BY public.categoria.id_categoria;


--
-- Name: cliente; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.cliente (
    id_cliente integer NOT NULL,
    nombre character varying(100),
    telefono character varying(15),
    email character varying(200)
);


ALTER TABLE public.cliente OWNER TO postgres;

--
-- Name: cliente_id_cliente_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.cliente_id_cliente_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.cliente_id_cliente_seq OWNER TO postgres;

--
-- Name: cliente_id_cliente_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.cliente_id_cliente_seq OWNED BY public.cliente.id_cliente;


--
-- Name: compra; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.compra (
    id_compra integer NOT NULL,
    fecha timestamp without time zone DEFAULT now(),
    nit character varying(200)
);


ALTER TABLE public.compra OWNER TO postgres;

--
-- Name: compra_id_compra_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.compra_id_compra_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.compra_id_compra_seq OWNER TO postgres;

--
-- Name: compra_id_compra_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.compra_id_compra_seq OWNED BY public.compra.id_compra;


--
-- Name: detalle_compra; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.detalle_compra (
    id_detalle_compra integer NOT NULL,
    id_compra integer,
    id_producto character varying(20),
    cantidad integer NOT NULL,
    precio_unidad numeric(10,2) NOT NULL,
    CONSTRAINT detalle_compra_cantidad_check CHECK ((cantidad >= 0)),
    CONSTRAINT detalle_compra_precio_unidad_check CHECK ((precio_unidad >= (0)::numeric))
);


ALTER TABLE public.detalle_compra OWNER TO postgres;

--
-- Name: detalle_compra_id_detalle_compra_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.detalle_compra_id_detalle_compra_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.detalle_compra_id_detalle_compra_seq OWNER TO postgres;

--
-- Name: detalle_compra_id_detalle_compra_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.detalle_compra_id_detalle_compra_seq OWNED BY public.detalle_compra.id_detalle_compra;


--
-- Name: detalle_venta; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.detalle_venta (
    id_detalle_venta integer NOT NULL,
    id_venta integer,
    id_producto character varying(20),
    cantidad integer NOT NULL,
    precio_unidad numeric(10,2) NOT NULL,
    CONSTRAINT detalle_venta_cantidad_check CHECK ((cantidad >= 0)),
    CONSTRAINT detalle_venta_precio_unidad_check CHECK ((precio_unidad >= (0)::numeric))
);


ALTER TABLE public.detalle_venta OWNER TO postgres;

--
-- Name: detalle_venta_id_detalle_venta_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.detalle_venta_id_detalle_venta_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.detalle_venta_id_detalle_venta_seq OWNER TO postgres;

--
-- Name: detalle_venta_id_detalle_venta_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.detalle_venta_id_detalle_venta_seq OWNED BY public.detalle_venta.id_detalle_venta;


--
-- Name: producto; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.producto (
    id_producto character varying(20) NOT NULL,
    nombre character varying(100) NOT NULL,
    precio numeric(10,2) NOT NULL,
    stock integer DEFAULT 0 NOT NULL,
    id_categoria integer,
    CONSTRAINT producto_precio_check CHECK ((precio >= (0)::numeric)),
    CONSTRAINT producto_stock_check CHECK ((stock >= 0))
);


ALTER TABLE public.producto OWNER TO postgres;

--
-- Name: proveedor; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.proveedor (
    nit character varying(200) NOT NULL,
    nombre character varying(100) NOT NULL,
    direccion character varying(150),
    ciudad character varying(100),
    contacto character varying(15)
);


ALTER TABLE public.proveedor OWNER TO postgres;

--
-- Name: venta; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.venta (
    id_venta integer NOT NULL,
    fecha timestamp without time zone DEFAULT now(),
    id_cliente integer
);


ALTER TABLE public.venta OWNER TO postgres;

--
-- Name: venta_id_venta_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.venta_id_venta_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.venta_id_venta_seq OWNER TO postgres;

--
-- Name: venta_id_venta_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.venta_id_venta_seq OWNED BY public.venta.id_venta;


--
-- Name: categoria id_categoria; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.categoria ALTER COLUMN id_categoria SET DEFAULT nextval('public.categoria_id_categoria_seq'::regclass);


--
-- Name: cliente id_cliente; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cliente ALTER COLUMN id_cliente SET DEFAULT nextval('public.cliente_id_cliente_seq'::regclass);


--
-- Name: compra id_compra; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.compra ALTER COLUMN id_compra SET DEFAULT nextval('public.compra_id_compra_seq'::regclass);


--
-- Name: detalle_compra id_detalle_compra; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.detalle_compra ALTER COLUMN id_detalle_compra SET DEFAULT nextval('public.detalle_compra_id_detalle_compra_seq'::regclass);


--
-- Name: detalle_venta id_detalle_venta; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.detalle_venta ALTER COLUMN id_detalle_venta SET DEFAULT nextval('public.detalle_venta_id_detalle_venta_seq'::regclass);


--
-- Name: venta id_venta; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.venta ALTER COLUMN id_venta SET DEFAULT nextval('public.venta_id_venta_seq'::regclass);


--
-- Data for Name: categoria; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.categoria (id_categoria, codigo, tipo) FROM stdin;
1	CAT1	papeleria
2	CAT2	alimentos
3	CAT3	snaks
4	CAT4	enbutidos
5	CAT5	licores
6	CAT6	aseo
8	CAT8	abarrotes
9	CAT9	lacteos
10	CAT10	medicamentos
11	CAT11	confiteria
12	CAT12	alimentos mascotas
7	CAT7	bebidas/gaseosas
\.


--
-- Data for Name: cliente; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.cliente (id_cliente, nombre, telefono, email) FROM stdin;
\.


--
-- Data for Name: compra; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.compra (id_compra, fecha, nit) FROM stdin;
\.


--
-- Data for Name: detalle_compra; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.detalle_compra (id_detalle_compra, id_compra, id_producto, cantidad, precio_unidad) FROM stdin;
\.


--
-- Data for Name: detalle_venta; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.detalle_venta (id_detalle_venta, id_venta, id_producto, cantidad, precio_unidad) FROM stdin;
\.


--
-- Data for Name: producto; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.producto (id_producto, nombre, precio, stock, id_categoria) FROM stdin;
7595	Submarino arequipe	1800.00	20	2
27768	Mnchitas	1800.00	20	2
41787	tostadas mant	3000.00	10	2
42177	brownie arequipe	2000.00	20	3
42193	brownie chocolate	2000.00	20	3
42443	cacero vainilla	3700.00	19	2
504660	panque vainilla	5000.00	5	2
506249	pan blanco pro	4000.00	4	2
506228	tajada rechocoli	1000.00	20	3
12294	glacitas fresa	1600.00	64	3
10851	chiricos pikantes	2200.00	5	2
13691	todo rico bbq	6000.00	5	2
13813	super crokantes original	6000.00	5	2
13673	papas fosforito	2000.00	7	3
13671	papas bbq	2200.00	5	3
13660	papas pollo	2200.00	8	3
1961	hit mango 500ml	4000.00	12	7
1962	hit mora500ml	4000.00	12	7
2801	hit mango 300ml	2000.00	12	7
3334	hit mora300ml	2000.00	12	7
984	azucar	2500.00	25	8
580050	nectar club	22000.00	5	5
580051	aguila x6	22000.00	24	5
580052	poker x6	22000.00	24	5
580053	coste?a	16000.00	20	5
580054	budweiser	16000.00	20	5
580055	club colombia dorada	22000.00	20	5
1001155	mortadela.zenu	3000.00	5	4
1029973	salchicha ranchera x3	4200.00	5	4
1043327	salchicha zenu x3	2500.00	5	4
1043657	salchichon cervecero zenu	2500.00	4	4
1046292	salchicha ranchera x5	5000.00	4	4
430956	kola granulada mk 	2500.00	12	10
640103	compota manzana	3000.00	6	8
640104	compota pera	3000.00	6	8
640684	salsa soya 	5000.00	6	8
190812	H&S reno	2500.00	12	6
870196	bianchi cho bols blanco	400.00	110	11
870197	bianchi cho bols	400.00	110	11
870296	muau pollo+salmon	10000.00	12	12
OFHAL002	advil fem	4100.00	10	10
MP08MC0003	acetaminofen 	2000.00	100	10
1952	cartulina 1/8	300.00	100	1
9628	lapiz negro	1200.00	36	1
22324	borrador blanco	500.00	20	1
37642	cinta transparendte med	800.00	24	1
136415	cocacola 500ml	4000.00	12	7
92768	brisa manzana 	2200.00	24	7
73441	sardinas 	8000.00	3	8
73442	pastillas raid	32000.00	24	8
7702511	arroz diana	2500.00	12	8
7509546	suavitel primavera	2000.00	4	6
720638	detergente floral	2000.00	4	6
720618	detergente bicarbonato manzana	2000.00	4	6
Y0198	Alquieria semi 400ml	2000.00	6	9
Y0363	Alquieria semi 900ml	4000.00	12	9
@GD052	fk vaso fresa	2500.00	4	9
@GD053	fk vaso melon	2500.00	4	9
59678	chochorramo	2000.00	10	3
\.


--
-- Data for Name: proveedor; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.proveedor (nit, nombre, direccion, ciudad, contacto) FROM stdin;
830.111.876-2	DISTRIBUIDORA EL FARO LTDA	Carrera 28Ş- #15-60 Paloquemao	Bogotá	601-3759300
830.002.366-0	BIMBO DE COLIMBIA S.A.	\N	Tenjo	601-6017452111
901.713.159-0	Comercializadora Super Ricas Sas	CALLE 10 NO. 38-120 BRR PANAMERICANO	Pasto	601-487 7979
83050703-8	CCENECA COMERCIAL SAS	Calle 19 # 69 f – 05 	Bogotá	3164633686
90.050.156-4	Comercializadora Jelbar S A S	KR 74 B # 49 A - 70	Bogotá	3165292797
890.302.594-9	Mayaguez S A	CALLE 22 NTE 6 AN 24 OF 701	Cali	6023691170
860.001.697-8	Gaseosas Lux S A S	CALLE 52 47 42 PISO 32	Medellín	6045765100
900.378.088-5	La Nacional De Licores De Colombia Sas	CALLE 19 B 5 14 ESTE	Mosquera	601-4325610
 830.047.819-9	Coca-Cola Bebidas de Colombia S.A.	Avenida Carrera 96 # 24c-94	Bogotá	3057702463
800.201.315-1	Surtilider S A S	CALLE 77 69 H 62	Bogotá	3167408580
860.004.922-4	Productos Naturales De La Sabana S A S Bic (Alquería)	VIA CAJICA TABIO KILOMETRO 5	Cajica	601-4887000
860.532.244-3	Zuluaga & Soto Sas	CARRERA 89 17 B 02 	Bogotá	601-4120120
601.748.200-0	Productos Ramo Sas	AVENIDA CALLE 116 7 15 INTERIOR 2 OFICINA 1502	Bogotá	601-7482000
900.267.777-5	Grupo R V Sas	CARRERA 77 37 18 SUR 	Bogotá	601-2884981
\.


--
-- Data for Name: venta; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.venta (id_venta, fecha, id_cliente) FROM stdin;
\.


--
-- Name: categoria_id_categoria_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.categoria_id_categoria_seq', 12, true);


--
-- Name: cliente_id_cliente_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.cliente_id_cliente_seq', 1, false);


--
-- Name: compra_id_compra_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.compra_id_compra_seq', 1, false);


--
-- Name: detalle_compra_id_detalle_compra_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.detalle_compra_id_detalle_compra_seq', 1, false);


--
-- Name: detalle_venta_id_detalle_venta_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.detalle_venta_id_detalle_venta_seq', 1, false);


--
-- Name: venta_id_venta_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.venta_id_venta_seq', 1, false);


--
-- Name: categoria categoria_codigo_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.categoria
    ADD CONSTRAINT categoria_codigo_key UNIQUE (codigo);


--
-- Name: categoria categoria_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.categoria
    ADD CONSTRAINT categoria_pkey PRIMARY KEY (id_categoria);


--
-- Name: cliente cliente_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cliente
    ADD CONSTRAINT cliente_email_key UNIQUE (email);


--
-- Name: cliente cliente_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cliente
    ADD CONSTRAINT cliente_pkey PRIMARY KEY (id_cliente);


--
-- Name: compra compra_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.compra
    ADD CONSTRAINT compra_pkey PRIMARY KEY (id_compra);


--
-- Name: detalle_compra detalle_compra_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.detalle_compra
    ADD CONSTRAINT detalle_compra_pkey PRIMARY KEY (id_detalle_compra);


--
-- Name: detalle_venta detalle_venta_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.detalle_venta
    ADD CONSTRAINT detalle_venta_pkey PRIMARY KEY (id_detalle_venta);


--
-- Name: producto producto_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.producto
    ADD CONSTRAINT producto_pkey PRIMARY KEY (id_producto);


--
-- Name: proveedor proveedor_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.proveedor
    ADD CONSTRAINT proveedor_pkey PRIMARY KEY (nit);


--
-- Name: venta venta_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.venta
    ADD CONSTRAINT venta_pkey PRIMARY KEY (id_venta);


--
-- Name: compra compra_nit_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.compra
    ADD CONSTRAINT compra_nit_fkey FOREIGN KEY (nit) REFERENCES public.proveedor(nit);


--
-- Name: detalle_compra detalle_compra_id_compra_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.detalle_compra
    ADD CONSTRAINT detalle_compra_id_compra_fkey FOREIGN KEY (id_compra) REFERENCES public.compra(id_compra);


--
-- Name: detalle_compra detalle_compra_id_producto_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.detalle_compra
    ADD CONSTRAINT detalle_compra_id_producto_fkey FOREIGN KEY (id_producto) REFERENCES public.producto(id_producto);


--
-- Name: detalle_venta detalle_venta_id_producto_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.detalle_venta
    ADD CONSTRAINT detalle_venta_id_producto_fkey FOREIGN KEY (id_producto) REFERENCES public.producto(id_producto);


--
-- Name: detalle_venta detalle_venta_id_venta_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.detalle_venta
    ADD CONSTRAINT detalle_venta_id_venta_fkey FOREIGN KEY (id_venta) REFERENCES public.venta(id_venta);


--
-- Name: producto producto_id_categoria_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.producto
    ADD CONSTRAINT producto_id_categoria_fkey FOREIGN KEY (id_categoria) REFERENCES public.categoria(id_categoria);


--
-- Name: venta venta_id_cliente_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.venta
    ADD CONSTRAINT venta_id_cliente_fkey FOREIGN KEY (id_cliente) REFERENCES public.cliente(id_cliente);


--
-- PostgreSQL database dump complete
--

\unrestrict ZrGjidFvxPBSYz1dc83iUSX57D2fd9uS4SWHLlhYC6uX9KKeOyy6z1Ne5KxOfnI

