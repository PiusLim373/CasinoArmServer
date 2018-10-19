import sys
import json

#print(sys.argv)
sum = int(sys.argv[1]) + int(sys.argv[2])
print(json.dumps({"players":[{"id":1,"position":{"distance":123.321,"angle":123.123}},{"id":2,"position":{"distance":456.654,"angle":456.456}},{"id":3,"position":{"distance":789,"angle":789}}]}))

