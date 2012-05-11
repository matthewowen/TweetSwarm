CREATE TABLE accounts(
	access_token varchar(255) primary key not null,
	access_secret varchar(255) not null
);

CREATE TABLE tweetswarms(
	name varchar(30) primary key not null,
	master varchar(30) not null,
	callsign varchar(30),
    lasttweeted varchar(30)
);

CREATE TABLE tweetswarmaccount(
	account_id varchar(255),
	tweetswarm varchar(255),
	FOREIGN KEY(account_id) REFERENCES accounts(access_token) ON DELETE CASCADE,
	FOREIGN KEY(tweetswarm) REFERENCES tweetswarms(name) ON DELETE CASCADE
);