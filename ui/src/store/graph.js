
import Vue from 'vue';
import Vuex from 'vuex';

Vue.use(Vuex);

export default new Vuex.Store({
  state: {
      resources : [],
      activities: [],
      allocatedLinks : [],
      containsLinks : [],
      constraints : [],
      resourceInstances : [],
      activityInstances : [],
      containsInstances : [],
      allocatedToInstances : [],
      rewards : {},
      budgets : {},
      costs : {}
},
  getters: {},
  mutations: {
    addResource(state, resourceObj) {
      state.resources.push(resourceObj)
    },
    addActivity(state, activityObj) {
      console.log("--> store addActivity: ")
      state.activities.push(activityObj);
      console.log("activityObj ", activityObj)
    },
    addAllocation(state, allocObj) {
      // --allocObj--
      // actName: actName,
      // existingResName: existingResName,
      console.log("--> store addAllocation: ")
      state.allocatedLinks.push(allocObj);
      console.log("allocObj ", allocObj)
      // console.log("state: ", state)
    }
  },
  actions: {}
});