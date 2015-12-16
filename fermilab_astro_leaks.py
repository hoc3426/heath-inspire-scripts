import re
from invenio.search_engine import perform_request_search
from invenio.search_engine import get_fieldvalues

search = "find a Adam Anderson \
or a Jim Annis \
or a Dan Bauer \
or a Bradford Benson \
or a Steve Brice \
or a E Buckley-Geer \
or a Ilias Cholis \
or a Aaron Chou \
or a Amy Cottle \
or a Mike Crisler \
or a Eric Dahl \
or a Tom Diehl \
or a Scott Dodelson \
or a Alex Drlica-Wagner \
or a Juan Estrada \
or a David Finley \
or a Brenna Flaugher \
or a Josh Frieman \
or a Hank Glass \
or a Nick Gnedin \
or a Erik Gottschalk \
or a Gaston Gutierrez \
or a Yann Guardincerri \
or a Seton Handville \
or a Craig Hogan \
or a Carlos Hojvat \
or a Dan Hooper \
#or a Lauren Hsu \
or a Steve Kent \
or a Rich Kron \
or a Donna Kubik \
or a Nikolay Kuropatkin \
or a Connie Lang \
or a Cathryn Laue \
or a Paul Lebrun \
or a Huan Lin \
or a Hugh Lippincott \
or a Ben Loer \
or a Pat Lukens \
or a Paul Mantsch \
or a John Marriner \
or a Peter Mazur \
or a Wyatt Merritt \
or a Eric H. Neilsen \
or a Hogan Nguyen \
or a Brian Nord \
or a John Peoples \
or a Stephen Pordes \
or a Rahlin \
or a Erik Ramberg \
or a Alan Robinson \
or a Marcelle Soares-Santos \
or a Vic Scarpine \
or a Andrew Sonnenschein \
or a Albert Stebbins \
or a Chris Stoughton \
or a Javier Tiffenberg \
or a Douglas Tucker \
or a William Wester \
or a Brian Yanny \
or a JongHee Yoo"
search += " not r fermilab"
search += " and (primarch astro-ph or astro-ph.he \
or astro-ph.co or astro-ph.GA \
or astro-ph.EP or astro-ph.IM \
or astro-ph.sr)"
print search

