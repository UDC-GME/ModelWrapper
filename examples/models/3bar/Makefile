ANALYSIS=analysis
POST=post
MESH=mesh
PARAMS=parameters.yaml

ifeq (${LOCAL},True)
	ASTER:=launchAster
else
	ASTER:=docker run -it  \
		   -v $$(pwd):/home/codeaster  -w /home/codeaster  \
		   registry.gitlab.com/miguelrsegade/librecae/codeaster \
		   launchAster
endif

all: $(POST).mess
init: $(MESH).geo $(ANALYSIS).comm $(POST).comm

# File initialization 
########################################
$(MESH).geo: $(PARAMS) $(MESH)_t.geo
	jprepro $^ $@
$(ANALYSIS).comm: $(PARAMS) $(ANALYSIS)_t.comm
	jprepro $^ $@
$(POST).comm: $(PARAMS) $(POST)_t.comm
	jprepro $^ $@
#########################################

$(MESH).med: $(MESH).geo
	gmsh -format med -1 $<

$(ANALYSIS).mess: $(ANALYSIS).export $(ANALYSIS).comm $(MESH).med
	$(ASTER) $(ANALYSIS).comm $(ANALYSIS).export

$(POST).mess: $(POST).export $(POST).comm $(ANALYSIS).mess
	$(ASTER) $(POST).comm $(POST).export

clean:
	rm -rf $(MESH).geo $(ANALYSIS).comm $(POST).comm
	rm -rf $(MESH).med
	rm -rf $(ANALYSIS).{base,mess}
	rm -rf $(POST).{resu,mess}
	rm -rf results.json
