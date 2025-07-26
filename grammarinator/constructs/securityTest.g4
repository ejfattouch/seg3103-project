grammar SecurityTestGrammar;

malicious_login : '{' email_field ',' password_field '}' ;

email_field : '"email"' ':' email_value ;
password_field : '"password"' ':' password_value ;

email_value : 
      quoted_nosql_injection
    | quoted_buffer_overflow
    | quoted_normal_email
    | mongo_operator_injection ;

password_value :
      quoted_xss_attack
    | quoted_buffer_overflow
    | quoted_normal_password
    | mongo_operator_injection ;

// Parser rules for quoted values
quoted_nosql_injection : '"' nosql_injection '"' ;
quoted_buffer_overflow : '"' buffer_overflow '"' ;
quoted_normal_email    : '"' normal_email '"' ;
quoted_xss_attack      : '"' xss_attack '"' ;
quoted_normal_password : '"' normal_password '"' ;

// Attack variants

nosql_injection:
      '{$ne": null}'
    | '{$gt": ""}'
    | '{$regex": ".*"}'
    | '{$where": "1==1"}'
    | '{$exists": true}' ;

mongo_operator_injection:
      '{$ne": "wrong"}'
    | '{$gt": ""}'
    | '{$lt": "zzzz"}'
    | '{$regex": "^.*"}'
    | '{$in": ["admin", "user"]}' ;

xss_attack:
      '<script>'
    | 'javascript:'
    | '<img src=x onerror='
    | '&lt;script&gt;' ;

buffer_overflow :
      CHUNK CHUNK CHUNK CHUNK CHUNK
    | CHUNK CHUNK CHUNK CHUNK CHUNK CHUNK
    | CHUNK CHUNK CHUNK CHUNK CHUNK CHUNK CHUNK CHUNK CHUNK CHUNK ; // 1000 chars

fragment CHUNK : [a-zA-Z0-9]{100} ;

normal_email : [a-zA-Z0-9_.+-]{1,20} '@' [a-zA-Z0-9.-]{1,20} '.' [a-zA-Z]{2,6} ;

// Enforce minimum 8 characters
fragment PASS_CHAR : [a-zA-Z0-9!@#$%^&*()_+=\-] ;
normal_password : PASS_CHAR PASS_CHAR PASS_CHAR PASS_CHAR PASS_CHAR PASS_CHAR PASS_CHAR PASS_CHAR (PASS_CHAR)* ;

// Whitespace
WS : [ \t\r\n]+ -> skip ;



