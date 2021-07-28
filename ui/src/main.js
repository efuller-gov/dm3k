import Vue from 'vue'
import Vuex from 'vuex';
import App from './App.vue'
import store from './store/graph';
import 'tabulator-tables/dist/css/tabulator.min.css';

Vue.use(Vuex);
Vue.config.productionTip = false

new Vue({
  store,
  render: h => h(App),
}).$mount('#app')