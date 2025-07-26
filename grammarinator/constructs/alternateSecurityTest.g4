grammar SecurityTestGrammar;

malicious_login : '{' attack_field (',' attack_field)* '}' ;

attack_field : 
    | '"email"' ':' '"' SQL_INJECTION '"'
    | '"password"' ':' '"' XSS_ATTACK '"'
    | '"email"' ':' '"' BUFFER_OVERFLOW '"'
    | '"' FIELD_INJECTION '"' ':' '"' NORMAL_VALUE '"'
    ;

SQL_INJECTION: '\'' [^']* '\'' | '1=1' | 'DROP TABLE' | 'UNION SELECT' ;
XSS_ATTACK: '<script>' | 'javascript:' | '<img src=x onerror=' ;
BUFFER_OVERFLOW: [a-zA-Z0-9]{1000,10000} ; // Extremely long strings
FIELD_INJECTION: '__proto__' | 'constructor' | 'prototype' ; // JS injection
NORMAL_VALUE: [a-zA-Z0-9!@#$%^&*()_+=\-]{5,20} ;