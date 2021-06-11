
import Vue from 'vue';
import Vuex from 'vuex';

Vue.use(Vuex);

export default new Vuex.Store({
  state: {
      resources : []
  },
  getters: {},
  mutations: {
    addResource(state, resource) {
        state.resources.push(resource);
        console.log("Within vuex. New state name is: ", resource)
        console.log("state: ", state)
      }
  },
  actions: {}
});