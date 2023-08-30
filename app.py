# TODO random country, better defaults
#################################################################################
# Learn about any country through this GPT-based app!
# 1. Choose a country to see its location and fun facts about it.
# 2. Ask the app to search Wikipedia to make sure it's not hallucinating.
# 3. Select which kinds of facts you're interested in like culture, sports, etst.
#
# To run the app, use the command:
# streamlit run appy
#
# Streamlit will run this file every time the user reloads the page 
# or modifies a dropdown, etst. Imported code is only run once though.
#################################################################################
## dependencies
import streamlit as st
# instantiated once
from api.model import model, all_fact_kinds
# instantiated once
from data.countries import all_countries, random_country_index

## app framework
def run():
    st.title('🌍 Country Facts')
    country = st.selectbox(label='What Country?', options=all_countries, index=random_country_index)
    fact_kinds = st.multiselect(label='What Kinds of Facts?', options=all_fact_kinds, default=['random', 'history', 'food'])
    use_wiki_choice = st.selectbox(label='Use Wikipedia?', options=['yes', 'no'], index=0)
    use_wiki = use_wiki_choice == 'yes'

    button_pressed = st.button('Run')
    st.header('_Results_ 🤓')

    if not button_pressed:
        return

    if not country or len(fact_kinds) == 0:
        st.write('please select a country and at least one kind of fact')
        return

    model.set_fact_kinds(fact_kinds)
    model.set_use_wiki(use_wiki)

    location, facts = model.get_country_facts(country)
    st.write('__Location:__ {}'.format(location))
    for kind, fact in zip(fact_kinds, facts):
        st.write('__Fun Fact ({}):__'.format(kind))
        st.write(fact)

    if use_wiki:
        all_research = model.get_current_research()
        for fact_kind, research in zip(fact_kinds, all_research):
            with st.expander('Wikipedia research on {}'.format(fact_kind)):
                st.info(research)

    with st.expander('Location History'): 
        st.info(model.get_location_memory())

run()
