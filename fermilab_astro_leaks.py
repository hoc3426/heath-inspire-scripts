import re
from invenio.search_engine import perform_request_search
from invenio.search_engine import get_fieldvalues

search = "find a Sein Ahn \
or a Sahar Allam \
or a Daniele Alves \
or a Jim Annis \
or a Dan Bauer \
or a Steve Brice \
or a M Buckley \
or a E Buckley-Geer \
or a Ilias Cholis \
or a Aaron Chou \
or a Mike Crisler \
or a Fritz DeJongh \
or a Tom Diehl \
or a Scott Dodelson \
or a Juan Estrada \
or a David Finley \
or a Brenna Flaugher \
or a Josh Frieman \
or a Hank Glass \
or a Nick Gnedin \
or a Erik Gottschalk \
or a Gaston Gutierrez \
or a Jeter Hall \
or a Jiangang Hao \
or a Andrew Hearin \
or a Craig Hogan \
or a Carlos Hojvat \
or a Dan Hooper \
or a Lauren Hsu \
or a Steve Kent \
or a E Kolb \
or a Rich Kron \
or a Donna Kubik \
or a Nikolay P. Kuropatkin \
or a Paul Lebrun \
or a Huan Lin \
or a Hugh Lippincott \
or a Ben Loer \
or a Paul Mantsch \
or a John Marriner \
or a Peter Mazur \
or a Wyatt Merritt \
or a Eric H. Neilsen, Jr. \
or a Hogan Nguyen \
or a Brian Nord \
or a John Peoples \
or a Stephen Pordes \
or a Erik Ramberg \
or a Marcelle Soares-Santos \
or a Vic Scarpine \
or a Andrew Sonnenschein \
or a Doug Spolyar \
or a Albert Stebbins \
or a Chris Stoughton \
or a Douglas Tucker \
or a William Wester \
or a Brian Yanny \
or a JongHee Yoo "
search = search + " not r fermilab and primarch astro-ph.*"
print search

