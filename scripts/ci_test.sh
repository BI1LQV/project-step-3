python setup.py install
export PYTHONPATH=$PYTHONPATH:$(pwd)
python -m coverage run test/test_Suite.py