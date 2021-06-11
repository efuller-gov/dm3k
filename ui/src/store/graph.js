
import Vue from 'vue';
import Vuex from 'vuex';

Vue.use(Vuex);

export default new Vuex.Store({
  state: {
      resources : []
  },
  getters: {},
  mutations: {
    addResource(state, resourceObj) {
        state.resources.push(resourceObj);
        console.log("state: ", state)
      }
  },
  actions: {}
});