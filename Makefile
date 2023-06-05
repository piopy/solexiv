.PHONY: install uninstall

greet:
	@echo "Ciao! Benvenuto nel Makefile."
	@echo ""
	@echo "1. make install \t\tInstalla l'applicazione"
	@echo "2. make uninstall \t\tDisinstalla l'applicazione"
	@echo ""

install:
	@echo "Eseguo l'installazione..."
	docker compose up --build -d
	@echo "Installazione completata con successo!"
	@echo "Vai su http://127.0.0.1:8181"

uninstall:
	@echo "Eseguo la disinstallazione..."
	@docker compose down --rmi all
	@echo "Disinstallazione completata con successo!"

default: greet
