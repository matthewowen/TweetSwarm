CREATE TABLE accounts(
	access_token varchar(255) primary key not null,
	access_secret varchar(255) not null
);

CREATE TABLE tweetnets(
	name varchar(255) primary key not null,
	master_account varchar(255) not null,
	callsign varchar(255) not null
);

CREATE TABLE tweetnetaccount(
	account_id varchar(255),
	tweetnet varchar(255),
	FOREIGN KEY(account_id) REFERENCES accounts(access_token) ON DELETE CASCADE,
	FOREIGN KEY(tweetnet) REFERENCES tweetnets(name) ON DELETE CASCADE
);