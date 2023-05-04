import Home from './pages/home.jsx';
import PanelLeft from './pages/panel-left.jsx';
import About from './pages/about.jsx';
import Files from './pages/files.jsx';
import Settings from './pages/settings.jsx';
import SignIn from './pages/sign-in.jsx';
import SignUp from './pages/sign-up.jsx';

import NotFound from './pages/404.jsx';

import store from './store';

function isAuthenticated({ resolve, reject }) {
  console.log('asdasdads');
  const router = this;
  if (!store.getters.isAuthenticated.value) {
    reject();
    router.navigate('/sign-in/');
  } else {
    resolve();
  }
}

function isNotAuthenticated({ resolve, reject }) {
  const router = this;
  if (store.getters.isAuthenticated.value) {
    reject();
    router.navigate('/');
  } else {
    resolve();
  }
}

export default [
  {
    path: '/',
    component: store.getters.isAuthenticated.value ? Home : SignIn,
    beforeEnter: isAuthenticated,
  },
  {
    path: '/sign-in/',
    component: !store.getters.isAuthenticated.value ? SignIn : Home,
    beforeEnter: isNotAuthenticated,
  },
  {
    path: '/sign-up/',
    component: !store.getters.isAuthenticated.value ? SignUp : Home,
    beforeEnter: isNotAuthenticated
  },
  {
    path: '/about/',
    component: store.getters.isAuthenticated.value ? About : SignIn,
    beforeEnter: isAuthenticated,
  },
  {
    path: '/panel-left/',
    component: store.getters.isAuthenticated.value ? PanelLeft : SignIn,
    beforeEnter: isAuthenticated,
  },
  {
    path: '/files/:fileId/',
    component: store.getters.isAuthenticated.value ? Files : SignIn,
    beforeEnter: isAuthenticated,
  },
  {
    path: '/settings/',
    component: store.getters.isAuthenticated.value ? Settings : SignIn,
    beforeEnter: isAuthenticated,
  },
  // Default route (404 page). MUST BE THE LAST
  {
    path: '(.*)',
    component: NotFound,
  },
];
