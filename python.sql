-- phpMyAdmin SQL Dump
-- version 5.1.3
-- https://www.phpmyadmin.net/
--
-- Servidor: mysql
-- Tiempo de generación: 07-04-2022 a las 18:00:40
-- Versión del servidor: 5.7.28
-- Versión de PHP: 8.0.15

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `python`
--
CREATE DATABASE IF NOT EXISTS `python` DEFAULT CHARACTER SET latin1 COLLATE latin1_swedish_ci;
USE `python`;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `compras`
--

DROP TABLE IF EXISTS `compras`;
CREATE TABLE IF NOT EXISTS `compras` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `descripcion` varchar(250) NOT NULL,
  `estado` varchar(50) NOT NULL,
  `empresa` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `FK_empresas` (`empresa`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `Empresas`
--

DROP TABLE IF EXISTS `Empresas`;
CREATE TABLE IF NOT EXISTS `Empresas` (
  `empresa` varchar(100) NOT NULL,
  PRIMARY KEY (`empresa`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `materia_objetos`
--

DROP TABLE IF EXISTS `materia_objetos`;
CREATE TABLE IF NOT EXISTS `materia_objetos` (
  `objeto_id` int(11) NOT NULL,
  `materia_id` int(11) NOT NULL,
  KEY `FK_Objetos` (`objeto_id`),
  KEY `FK_materia` (`materia_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `materia_prima`
--

DROP TABLE IF EXISTS `materia_prima`;
CREATE TABLE IF NOT EXISTS `materia_prima` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) NOT NULL,
  `descripcion` varchar(250) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `objetos`
--

DROP TABLE IF EXISTS `objetos`;
CREATE TABLE IF NOT EXISTS `objetos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) NOT NULL,
  `descripcion` varchar(250) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `Produccion`
--

DROP TABLE IF EXISTS `Produccion`;
CREATE TABLE IF NOT EXISTS `Produccion` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `descripcion` varchar(250) NOT NULL,
  `cantidad` int(11) NOT NULL,
  `objeto_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `FK_objeto_produccion` (`objeto_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `Usuarios`
--

DROP TABLE IF EXISTS `Usuarios`;
CREATE TABLE IF NOT EXISTS `Usuarios` (
  `usuario` varchar(50) NOT NULL,
  `clave` varchar(300) NOT NULL,
  `permisos` varchar(50) NOT NULL,
  `departamento` varchar(50) NOT NULL,
  PRIMARY KEY (`usuario`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Volcado de datos para la tabla `Usuarios`
--

INSERT INTO `Usuarios` (`usuario`, `clave`, `permisos`, `departamento`) VALUES
('Admin', 'Admin', 'Admin', 'Jefe');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `ventas`
--

DROP TABLE IF EXISTS `ventas`;
CREATE TABLE IF NOT EXISTS `ventas` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `descripcion` varchar(250) NOT NULL,
  `estado` varchar(50) NOT NULL,
  `empresa` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `FK_empresas_ventas` (`empresa`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `compras`
--
ALTER TABLE `compras`
  ADD CONSTRAINT `FK_empresas` FOREIGN KEY (`empresa`) REFERENCES `Empresas` (`empresa`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Filtros para la tabla `materia_objetos`
--
ALTER TABLE `materia_objetos`
  ADD CONSTRAINT `FK_Objetos` FOREIGN KEY (`objeto_id`) REFERENCES `objetos` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `FK_materia` FOREIGN KEY (`materia_id`) REFERENCES `materia_prima` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Filtros para la tabla `Produccion`
--
ALTER TABLE `Produccion`
  ADD CONSTRAINT `FK_objeto_produccion` FOREIGN KEY (`objeto_id`) REFERENCES `objetos` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Filtros para la tabla `ventas`
--
ALTER TABLE `ventas`
  ADD CONSTRAINT `FK_empresas_ventas` FOREIGN KEY (`empresa`) REFERENCES `Empresas` (`empresa`) ON DELETE CASCADE ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
