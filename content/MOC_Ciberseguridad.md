---
title: MOC Ciberseguridad
date: 2026-06-14
tags: [ciberseguridad, programacion/seguridad, moc]
type: moc
status: en-progreso
source: claude-code
aliases: [MOC Ciberseguridad, Ciberseguridad MOC, MOC Seguridad]
---

# MOC Ciberseguridad

> Mapa de **ciberseguridad**: fundamentos, criptografía, redes, seguridad web (OWASP),
> identidad, sistemas, pentesting (ético), DevSecOps, blue team, privacidad y carrera.
> Clúster en `50_Areas/Ingenieria/Programacion/Ciberseguridad/`.
>
> Área padre: [[MOC_Programacion]] · Teoría base: [[MOC_CS_Fundamentos]]
>
> **Ética**: todo aquí es para **defender** y para pentesting **autorizado** (tus sistemas, labs, CTFs).

## Índice y registros vivos
- [[Ciberseguridad/00_README|README del clúster]] — qué es y cómo recorrerlo
- [[Ciberseguridad/00_Dudas_y_Preguntas|Dudas y Preguntas]]
- [[Bandit/00_README|OverTheWire Bandit]] — práctica de terminal/CTF: guía + walkthroughs (0-33) + tabla de progreso
- [[Leviathan/00_README|OverTheWire Leviathan]] — siguiente paso tras Bandit: binarios setuid, `ltrace`, symlinks (0-7)
- [[Natas/00_README|OverTheWire Natas]] — **seguridad web** (OWASP) jugando: walkthroughs de los 34 niveles
- [[HTB_Starting_Point/00_README|HackTheBox Starting Point]] — primeras máquinas Very Easy (Tier 0-2): 25 writeups + **síntesis de patrones/teoría**
- (facil) [[HTB_Easy/00_README|HackTheBox máquinas Easy]] — el paso siguiente: 15 máquinas retiradas (cadena foothold→shell→privesc) + patrones
- (media) [[HTB_Medium/00_README|HackTheBox máquinas Medium]] — 5 ejemplos ultra-detallados (NoSQLi, polyglot, AD/Kerberoasting…) para ver cómo se encadenan

## Documentación por tema
| #   | Tema                                                                       | Doc                                      |
| --- | -------------------------------------------------------------------------- | ---------------------------------------- |
| 01  | Fundamentos y mentalidad (CIA, threat modeling, ética)                     | [[01-fundamentos-y-mentalidad]]          |
| 02  | Criptografía (simétrica/asimétrica, TLS/PKI, hashing)                      | [[02-criptografia]]                      |
| 03  | Seguridad de redes (firewalls, VPN, nmap, Wireshark)                       | [[03-seguridad-de-redes]]                |
| 04 | **Seguridad web — OWASP Top 10** | [[04-seguridad-web-owasp]] |
| 05  | Identidad: auth, authz y secretos (JWT, OAuth2, MFA)                       | [[05-identidad-auth-y-secretos]]         |
| 06  | Seguridad de sistemas y hardening                                          | [[06-seguridad-de-sistemas-y-hardening]] |
| 07  | Pentesting y el ciclo del ataque (MITRE ATT&CK)                            | [[07-pentesting-y-ciclo-del-ataque]]     |
| 08  | Vulnerabilidades y explotación (CVE/CVSS, conceptual)                      | [[08-vulnerabilidades-y-explotacion]]    |
| 09  | DevSecOps y AppSec (SAST/DAST/SCA, supply chain)                           | [[09-devsecops-y-appsec]]                |
| 10  | Blue team y respuesta a incidentes (SOC, SIEM, IR)                         | [[10-blue-team-y-respuesta-incidentes]]  |
| 11  | Privacidad y OPSEC (Tor, threat model personal)                            | [[11-privacidad-y-opsec]]                |
| 12  | Aprender y carrera (labs, CTFs, certs, roles)                              | [[12-aprender-y-carrera]]                |
| 13 | **Herramientas en detalle** (nmap, gobuster, Burp, hydra, nc, LinPEAS…) | [[13-herramientas-en-detalle]] |

## Roadmap de aprendizaje
1. **Base**: [[01-fundamentos-y-mentalidad]] → [[02-criptografia]] → [[03-seguridad-de-redes]].
2. **Lo de más ROI para ti (dev)** : [[04-seguridad-web-owasp]] → [[05-identidad-auth-y-secretos]] → [[09-devsecops-y-appsec]] (asegura tus y tu CI/CD).
3. **Ofensiva/sistemas**: [[06-seguridad-de-sistemas-y-hardening]] → [[07-pentesting-y-ciclo-del-ataque]] → [[08-vulnerabilidades-y-explotacion]].
4. **Defensa y carrera**: [[10-blue-team-y-respuesta-incidentes]], [[11-privacidad-y-opsec]], y [[12-aprender-y-carrera]] (lab + CTFs + certs).
5. **Aprende haciendo**: lab en VMs (Kali + DVWA/Metasploitable) + **OverTheWire Bandit** ([[Bandit/00_README|guía + walkthroughs niveles 0-5]]) + **TryHackMe** + **PortSwigger Academy**.

## Conexiones
- [[MOC_Programacion]] — área raíz
- [[MOC_CS_Fundamentos]] — teoría (redes, OS, concurrencia)
- [[MOC_GitLab]] · [[MOC_Desarrollo_Software]] — DevSecOps / CI-CD seguro
