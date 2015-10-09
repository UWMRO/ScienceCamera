SUBDIRS = cooling fvb generic kinseries multitrack randomtrack rta shamrock

.PHONY: all

subdirs:
	for dir in $(SUBDIRS); do \
		$(MAKE) -C $$dir; \
	done

subdirs_clean:
	for dir in $(SUBDIRS); do \
		$(MAKE) -C $$dir clean; \
	done

all: subdirs

clean: subdirs_clean


