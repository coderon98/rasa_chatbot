DOMAIN = --domain domain/
CREDIT = --credentials credentials.yml


train:
	rasa train nlu ;
	rasa train $(DOMAIN) ;
	clear;

run:
	clear;
	rm -f models/*.gz;
	rasa train nlu ;
	clear;
	rasa train  $(DOMAIN);
	clear;
	rasa run --debug $(CREDIT)

test:
	rasa test
