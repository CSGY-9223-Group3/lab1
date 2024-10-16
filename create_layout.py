# create_layout.py

from securesystemslib.signer import CryptoSigner
from in_toto.models.layout import Layout, Step, Inspection
from in_toto.models.metadata import Metablock
import datetime

# Generate in-memory keys for project owner and functionary
project_owner = CryptoSigner.generate_ed25519()
functionary = CryptoSigner.generate_ed25519()

# Create an empty layout
layout = Layout()

# Add functionary public key to the layout
key_dict = functionary.public_key.to_dict()
key_dict["keyid"] = functionary.public_key.keyid
layout.add_functionary_key(key_dict)

# Set expiration date (e.g., 4 months from now)
layout.set_relative_expiration(months=4)

# Create the build step
step_build = Step(name="build")
step_build.pubkeys = [functionary.public_key.keyid]
step_build.expected_command = [
    "bash",
    "-c",
    "docker build -t pastebin:latest . && docker save pastebin:latest -o docker-image.tar",
]
step_build.expected_materials = [["ALLOW", "*"]]
step_build.expected_products = [["CREATE", "docker-image.tar"], ["DISALLOW", "*"]]

# Add the step to the layout
layout.steps.append(step_build)

# Create an inspection (optional)
inspection = Inspection(name="verify-image")
inspection.run = ["docker", "load", "-i", "docker-image.tar"]
inspection.expected_materials = [
    ["MATCH", "docker-image.tar", "WITH", "PRODUCTS", "FROM", "build"]
]
inspection.expected_products = [["ALLOW", "*"]]

# Add the inspection to the layout
layout.inspect.append(inspection)

# Wrap the layout in a Metablock and sign it with the project owner's key
metablock = Metablock(signed=layout)
metablock.create_signature(project_owner)
metablock.dump("root.layout")
