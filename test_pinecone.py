# test_pinecone.py
from pinecone import Pinecone
pc = Pinecone(api_key="pcsk_4GyaVR_8FBiw9SEMNiL99ssnQQztyGAokkg7kTLJdMpkfdXfmSGNdzhKzYRK2zRCp3EHzf")
print(pc.list_indexes())