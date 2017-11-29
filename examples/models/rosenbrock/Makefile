all: results.json

rosen: rosen.cpp
	g++ -o $@ -lyaml-cpp -ljsoncpp $<	

results.json: rosen parameters.yaml
	./rosen 

clean:
	rm -rf rosen results.json
