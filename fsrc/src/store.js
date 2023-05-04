import { createStore } from 'framework7';

const store = createStore({
  state: {
    auth: {
      accessToken: localStorage.getItem('accessToken') || null,
      refreshToken: localStorage.getItem('refreshToken') || null,
    },
    isAuthenticated: localStorage.getItem('accessToken') !== null ? true : false,
  },
  getters: {
    accessToken({ state }) {
      return state.auth.accessToken;
    },
    refreshToken({ state }) {
      return state.auth.refreshToken;
    },
    isAuthenticated({ state }) {
      return state.isAuthenticated;
    },
  },
  actions: {
    setIsAuthenticated({ state }, IsAuthenticated) {
      state.IsAuthenticated = IsAuthenticated;
    },
    setAccessToken({ state }, accessToken) {
      localStorage.setItem("accessToken", accessToken)
      state.auth.accessToken = accessToken;
    },
    setRefreshToken({ state }, refreshToken) {
      localStorage.setItem("refreshToken", refreshToken)
      state.auth.refreshToken = refreshToken;
    },
  },
});

export default store;
