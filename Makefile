env/made: requirements.txt
	$(RM) -rf $(@D)
	python3 -m venv $(@D) \
	&& . ./$(@D)/bin/activate \
	&& ./$(@D)/bin/pip install -r $<
	touch $@

.PHONY: clean
clean:
	$(RM) -rf env
