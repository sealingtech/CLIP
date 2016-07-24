#!/bin/bash

#Assume we are running from the root of the CLIP repo to make live easy

configs=(`find support/tests/bootstrap -type f -iname "*-bootstrap.conf"`)
result=1
pass=0
fail=0
test_count=${#configs[@]}
echo "Found ${tst_count} configs to test"
for (( conf=0; conf<${test_count};  conf++ ));
do
	case_type=""
	case="${configs[${conf}]}"
	if [[ ${case} =~ (good|bad)-.*bootstrap.conf ]]; then
		case_type=${BASH_REMATCH[1]}
	else
		echo "Couldn't determine whether ${case} is expected to pass or fail"
	fi
	case ${case_type} in
		good)
			echo "Running expected pass test: ${case}"
			sudo ./bootstrap.sh -c ${case}
			result=$?
			if [ $result -eq 0 ]; then
				echo "Test ${case}: Passed"
				pass=$((pass+1))
			else
				echo "Test ${case}: Failed"
				fail=$((fail+1))
			fi
			;;
		#We expect these to fail; hence the inverted logic
		bad)
			echo "Running expected failure test: ${case}"
			sudo ./bootstrap.sh -c ${case}
			result=$?
			if [ $result -eq 0 ]; then
				echo "Test ${case}: Failed"
				fail=$((fail+1))
			else
				echo "Test ${case}: Passed"
				pass=$((pass+1))

			fi
			;;
		[^\(good\|bad\)])
			echo "Skipping test case ${case}; Try renaaming to good-<descriptive_name>-bootstrap.conf"
			echo "or bad-<descriptive-name>-bootstrap.conf"
			exit 1
			;;
	esac
done
echo "Ran ${test_count} Tests. Passed: ${pass} Failed: ${fail}"
if [ "$pass" -eq "$test_count" ]; then
	echo "Passed"
	result=0
else
	echo "Failed"
	result=1
fi
exit $result
