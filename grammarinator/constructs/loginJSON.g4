grammar LoginJSON;

json       : '{' email ',' password '}' ;
email      : '"email"' ':' '"' EMAIL_STRING '"' ;
password   : '"password"' ':' '"' password_chars '"' ;

EMAIL_STRING: [a-zA-Z0-9_.+-]+ '@' [a-zA-Z0-9.-]+ '.' [a-zA-Z]+ ;

fragment PASS_CHAR : [a-zA-Z0-9!@#$%^&*()_+=\-] ;
password_chars : PASS_CHAR PASS_CHAR PASS_CHAR PASS_CHAR PASS_CHAR PASS_CHAR PASS_CHAR PASS_CHAR (PASS_CHAR)* ; // at least 8.

WS : [ \t\r\n]+ -> skip ;
