grammar ValidationTestGrammar;

// Entry point
login_test : valid_login | edge_login | invalid_login ;

// Valid inputs
valid_login : '{' '"email"' ':' quoted_VALID_EMAIL ',' '"password"' ':' quoted_VALID_PASSWORD '}' ;

// Edge case inputs
edge_login : '{' '"email"' ':' quoted_EDGE_EMAIL ',' '"password"' ':' quoted_EDGE_PASSWORD '}' ;

// Invalid inputs
invalid_login : '{' '"email"' ':' quoted_INVALID_EMAIL ',' '"password"' ':' quoted_INVALID_PASSWORD '}' ;

// Quoted value wrappers
quoted_VALID_EMAIL    : '"' VALID_EMAIL '"' ;
quoted_VALID_PASSWORD : '"' VALID_PASSWORD '"' ;

quoted_EDGE_EMAIL     : '"' EDGE_EMAIL '"' ;
quoted_EDGE_PASSWORD  : '"' EDGE_PASSWORD '"' ;

quoted_INVALID_EMAIL  : '"' INVALID_EMAIL '"' ;
quoted_INVALID_PASSWORD : '"' INVALID_PASSWORD '"' ;

// VALID email/password
VALID_EMAIL : EMAIL_LOCAL_PART '@' EMAIL_DOMAIN '.' EMAIL_TLD ;
VALID_PASSWORD : PASSWORD_CHAR+ ;

// EDGE email/password (boundary testing)
EDGE_EMAIL : EDGE_EMAIL_LOCAL '@' EDGE_EMAIL_DOMAIN '.' EDGE_EMAIL_TLD ;
EDGE_PASSWORD : PASSWORD_CHAR{8} | PASSWORD_CHAR{20} ;

// INVALID email/password
INVALID_EMAIL : SHORT_STRING | MISSING_AT_OR_DOMAIN ;
INVALID_PASSWORD : PASSWORD_CHAR{1,4} ;

// Components for VALID/EDGE/INVALID emails
fragment EMAIL_LOCAL_PART : EMAIL_CHAR{1,20} ;
fragment EMAIL_DOMAIN     : EMAIL_CHAR{1,20} ;
fragment EMAIL_TLD        : [a-zA-Z]{2,6} ;

fragment EDGE_EMAIL_LOCAL : EMAIL_CHAR{64} ;
fragment EDGE_EMAIL_DOMAIN: EMAIL_CHAR{63} ;
fragment EDGE_EMAIL_TLD   : [a-zA-Z]{6} ;

fragment SHORT_STRING : EMAIL_CHAR{0,5} ;
fragment MISSING_AT_OR_DOMAIN : EMAIL_CHAR{1,10} ;

// Characters allowed
fragment EMAIL_CHAR : [a-zA-Z0-9_.+-] ;
fragment PASSWORD_CHAR : [a-zA-Z0-9!@#$%^&*()_+=\-] ;

// Whitespace
WS : [ \t\r\n]+ -> skip ;



