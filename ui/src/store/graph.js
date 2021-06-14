
import Vue from 'vue';
import Vuex from 'vuex';

Vue.use(Vuex);

export default new Vuex.Store({
  state: {
      resources : [],
      activities: [],
      allocatedLinks : []
  },
  getters: {},
  mutations: {
    addResource(state, resourceObj) {
        state.resources.push(resourceObj);
        console.log("state: ", state)
      },
    addActivity(state, activityObj) {
        state.activities.push(activityObj);
        console.log("state: ", state)
      },
    addAllocation(state, activityObj) {
        state.activities.push(activityObj);
        console.log("state: ", state)
      }
  },
  actions: {}
});