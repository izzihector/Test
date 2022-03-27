MyPipAppraisalParent = {
  props: ["id"],
  data() {
    return {
      currentComponent: "PIPFullForm",
      dataLoading: true,
      dataExists: false,
      appraisalData: {},
      error: false,
      message: "",
      messageType: "success",
      flash: false,
      hasAccess: true,
      hasAccessMessage: "",
    };
  },
  methods: {
    toggleChat(val) {
      document.querySelector("#invoice_communication").style.display = val;
    },
    async submitForm(data) {
      try {
        result = await fetch("/employee/update-my-pip-appraisals", {
          method: "POST",
          headers: {
            Accept: "application/json",
            "Content-Type": "application/json",
          },
          body: JSON.stringify(data),
        });
        jsonResponse = await result.json();

        // ODOO Error Catch
        if (jsonResponse.error) {
          throw new Error(
            `${jsonResponse.error.message} - ${jsonResponse.error.data.message}`
          );
        }
        // Custom Error Catch
        responseData = JSON.parse(jsonResponse.result);
        if (responseData.update_status == "fail") {
          throw new Error(`${responseData.errors}`);
        }
        await this.getData();
        this.showMessage((message = "Saved Successfully!"), (type = "success"));
      } catch (e) {
        this.showMessage((message = e), (type = "error"));
        return false;
      }
      return true;
    },
    async getData() {
      try {
        result = await fetch("/employee/get-my-pip-appraisals", {
          method: "POST",
          headers: {
            Accept: "application/json",
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ appraisal_pip_id: this.id }),
        });
        jsonResponse = await result.json();
        if (jsonResponse.error) {
          throw new Error(
            `${jsonResponse.error.message} - ${jsonResponse.error.data.message}`
          );
        }
        this.appraisalData = JSON.parse(jsonResponse.result);
      } catch (e) {
        this.showMessage((message = e), (type = "error"));
      }
      this.dataLoading = false;
      if (Object.keys(this.appraisalData).length > 0) {
        console.log(">>>>>> after quey data", this.appraisalData);
        this.dataExists = true;
        this.change_component("PIPFullForm");
        this.setAccessInfo();
      }
    },
    change_component(data) {
      this.currentComponent = data;
      this.setAccessInfo();
      this.toggleChat("block");
    },
    setAccessInfo() {
      this.hasAccess = this.appraisalData.metaInfo.hasCurrentComponentAccess;
      this.hasAccessMessage =
        this.appraisalData.metaInfo.hasCurrentComponentAccessMessage;
    },
    showMessage(message, type) {
      if (type == "error") {
        this.error = true;
      }
      this.message = message;
      this.messageType = type;
      this.flash = true;
    },
    closeMessage() {
      this.flash = false;
      this.message = "";
      this.messageType = "success";
      this.error = false;
    },
  },
  provide() {
    return {
      appraisalData: Vue.computed(() => this.appraisalData),
      currentComponent: Vue.computed(() => this.currentComponent),
      submitFunction: this.submitForm,
      changeComponent: this.change_component,
      showFlashMessage: this.showMessage,
      closeFlashMessage: this.closeMessage,
      toggleChat: this.toggleChat,
    };
  },
  components: {
    "side-bar": PipSideBarComponent,
    MSetPipObjectives,
    MSetPipReviews,
    PIPSubmitForm,
    PIPFullForm,
    FlashMessage,
    LoadingComponent,
    BreadCrumb,
  },
  mounted() {
    console.log(">>>>> welcome idaaaaaaaaa", this.id);
    this.getData();
  },
  template: `
        <div style="width:100%; margin-top: -17px" v-if="!dataLoading && dataExists && hasAccess">
            <div class="row bg-white mt-2">
                <div class="col-lg-3 border-grey border py-1 px-2 custom_font_size" >Employee Name:</div>
                <div class="col-lg-9 border-grey border py-1 px-2 custom_font_size">{{ appraisalData.employee_name }}</div>
                
            </div>
            <div class="row bg-white">
                <div class="col-lg-3 border-grey border py-1 px-2 custom_font_size">Position</div>
                <div class="col-lg-9 border-grey border py-1 px-2 custom_font_size">{{ appraisalData.position }}</div>
            </div>
            <div class="row bg-white">
                <div class="col-lg-3 border-grey border py-1 px-2 custom_font_size">Supervisor(s)</div>
                <div class="col-lg-9 border-grey border py-1 px-2 custom_font_size"> {{ appraisalData.manager_name }} </div>
            </div>
            <div class="row bg-white">
                <div class="col-lg-3 border-grey border py-1 px-2 custom_font_size">Date of initial Meeting</div>
                <div class="col-lg-9 border-grey border py-1 px-2 custom_font_size"> {{ appraisalData.initial_meeting_date }} </div>
            </div>
            <div class="row bg-white">
                <div class="col-lg-3 border-grey border py-1 px-2 custom_font_size">Name(s) of other attendee (s)</div>
                <div class="col-lg-9 border-grey border py-1 px-2 custom_font_size"> 
                    <span v-for="atten in appraisalData.other_attendees_names ">
                        {{ atten }}, 
                    </span> 
                </div>
            </div>
        </div>
        <div class="row my-5">
            <BreadCrumb :state="appraisalData.state" v-if="!dataLoading && dataExists" appraisalType="pipAppraisal"/>
            <div class="col-lg-3 py-5 pl-4 bg-white bd-right-grey" v-if="!dataLoading && dataExists  && hasAccess">
                <side-bar @change_component="change_component" sideBarType="employees"/>
            </div>
            <div :class="{'col-lg-9': dataExists, 'col-lg-12': !dataExists || !hasAccess}" class="py-2 p-lg-5" style="background: white; min-height: 400px;">
                <template v-if="!dataLoading && dataExists">
                    <transition name="component-fade" mode="out-in">
                        <div class="alert custom_alert text-center d-block" v-if="!hasAccess">
                            {{ hasAccessMessage }}
                        </div>  
                    </transition>
                    <transition name="component-fade" mode="out-in">
                        <component :is="currentComponent" submit-type='byManager'></component>
                    </transition>
                </template>
                <LoadingComponent v-if="dataLoading && !error"/>
                <div v-if="!dataExists && !dataLoading && !error">
                    <h4>No Appraisal Record Found!</h4>
                </div>
            </div>
            <FlashMessage :message='message' v-if="flash" :type='messageType' @close-message='closeMessage' ></FlashMessage>
        </div>
  
    `,
};
const my_pip_appraisal_app = Vue.createApp({});

my_pip_appraisal_app.component("my-pip-appraisal-parent", MyPipAppraisalParent);
my_pip_appraisal_app.mount("#vue_pip_my_appraisal_app");
