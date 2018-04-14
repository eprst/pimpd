env/made: requirements.txt
	$(RM) -rf $(@D)
	virtualenv $(@D) \
	&& . ./$(@D)/bin/activate \
	&& ./$(@D)/bin/pip install -r $<
	touch $@

.PHONY: clean
clean:
	$(RM) -rf env