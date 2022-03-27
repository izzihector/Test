MSetPipReviews = {
    inject: ['appraisalData', 'submitFunction', 'showFlashMessage', 'changeComponent', 'toggleChat'],
    data() {
        return {
            formData: {},
            disableButton: false,
            buttonText: "Save and next",
            total_list_reviews_length: 0,
            readOnlyMode: true,
            editButtonText: "Edit",
            creteriaDict: {}
        }
    },
    watch: {
        total_list_reviews_length: {
            handler(newVal, oldVal) {
                if (newVal > 5) {
                    this.total_list_reviews_length = 5
                    this.showFlashMessage(message="Max Five Reviews can be set.", type="error")
                }else {
                    
                    lenReviews = Object.keys(this.formData['set_reviews']).length
                    if (this.total_list_reviews_length > lenReviews) {
                        let allowAdd = true
                        Object.values(this.formData['set_reviews']).forEach(obj => {
                            if (obj.finalized == false) {
                                this.total_list_reviews_length--
                                this.showFlashMessage(message="Can not set more than one unfinzalized review date.", type="error")
                                allowAdd = false
                            }
                        });
                        if (!allowAdd) {
                            return
                        }
                        this.formData.set_reviews['review_'+ lenReviews] = {
                            id: null,
                            review_date: '',
                            notes: '',
                            result: '',
                            finalized: false,
                        }
                    }
                }
            },
            immediate: false
        },
        appraisalData: {
            handler(newVal, oldVal) {
                if (newVal.value) this.writeDataToForm(newVal)
            },
            immediate: true,
            deep: true
        },
    },
    methods: {
        changeReadOnlyMode(changeData=true) {
            this.readOnlyMode = !this.readOnlyMode
            if (this.readOnlyMode) {
                this.toggleChat('block')
                this.editButtonText = "Edit"
                if (changeData) this.writeDataToForm(this.appraisalData)
            }else {
                this.editButtonText = "Discard"
                this.toggleChat('none')
            }
        },
        writeDataToForm(data) {
            this.formData['set_reviews'] = {}
            this.formData['appraisal_pip_id'] = data.value['id']
            this.formData['setting_reviews'] = true
            this.creteriaDict = data.value.creteria_dict
            if (data.value['reviews']) {
                lenReviews = Object.keys(data.value['reviews']).length
                if (lenReviews > 0) {
                    data.value['reviews'].forEach((obj, index) => {
                        this.formData.set_reviews['review_'+ index] = {
                            id: obj.id,
                            review_date: obj.review_date,
                            notes: obj.notes,
                            result: obj.result,
                            finalized: obj.finalized,
                        }
                    });
                    this.total_list_reviews_length =  lenReviews
                }
            }
        },
        async submitForm() {
            this.disableButton = true
            this.buttonText = "Saving..."
            result = await this.submitFunction(this.formData)
            if (result) {
                this.changeReadOnlyMode(changeData=false)
                if ((this.appraisalData.value.state == 'assessment' && this.appraisalData.value.metaInfo.setting_pip_review_assessment_state) 
                    || (this.appraisalData.value.state == 'planning' && this.appraisalData.value.metaInfo.setting_pip_review_state)){
                    this.changeComponent('PIPSubmitForm')
                }
            }
            this.disableButton = false
            if (this.appraisalData.value.state == 'performance_period') {
                this.buttonText = 'Save'
            } else {
                this.buttonText = 'Save and next'
            }
        },
    },
    template: `
        <div>
            <h4 style="font-size: 20px;background: #ffffff;padding: 10px 0;margin-top: 20px;border-bottom: 4px solid #875a7b;text-transform: uppercase;">
                Target Dates and Review Notes
            </h4>
            <div class="text-center">
                <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" data-name="Layer 1" width="200" height="200" viewBox="0 0 631.48281 593.94092"><path d="M790.35308,612.97046a26,26,0,1,1,26-26A26.02948,26.02948,0,0,1,790.35308,612.97046Z" transform="translate(-284.2586 -153.02954)" fill="#ccc"/><path d="M802.35308,585.97046h-11v-12.5a1,1,0,0,0-2,0v12.5h-11a1,1,0,1,0,0,2h11v12.5a1,1,0,0,0,2,0v-12.5h11a1,1,0,0,0,0-2Z" transform="translate(-284.2586 -153.02954)" fill="#fff"/><polygon points="606.22 581.779 594.788 581.778 589.352 537.682 606.224 537.683 606.22 581.779" fill="#ffb8b8"/><path d="M586.622,578.511h22.04782a0,0,0,0,1,0,0V592.393a0,0,0,0,1,0,0H572.74007a0,0,0,0,1,0,0v0A13.88193,13.88193,0,0,1,586.622,578.511Z" fill="#2f2e41"/><polygon points="560.72 581.779 549.288 581.778 543.852 537.682 560.724 537.683 560.72 581.779" fill="#ffb8b8"/><path d="M541.122,578.511h22.04782a0,0,0,0,1,0,0V592.393a0,0,0,0,1,0,0H527.24007a0,0,0,0,1,0,0v0A13.88193,13.88193,0,0,1,541.122,578.511Z" fill="#2f2e41"/><path d="M899.28547,582.35785a9.377,9.377,0,0,1,1.97614-14.242l-3.54086-21.13341,12.31791-5.28408,4.5812,29.9147a9.42779,9.42779,0,0,1-15.33439,10.74481Z" transform="translate(-284.2586 -153.02954)" fill="#ffb8b8"/><path d="M802.84749,572.37212a9.377,9.377,0,0,0,.40388-14.37279l6.98357-20.25805-11.27569-7.24646-9.46034,28.74681a9.42779,9.42779,0,0,0,13.34858,13.13049Z" transform="translate(-284.2586 -153.02954)" fill="#ffb8b8"/><circle cx="577.1393" cy="245.54228" r="24.56103" fill="#ffb8b8"/><path d="M802.08818,557.21623a4.50221,4.50221,0,0,1-1.24536-.17627l-7.15869-2.05517a4.50764,4.50764,0,0,1-3.08765-5.55127l14.77368-52.16211,20.60206-50.5752c2.04858-5.02783,6.32861-8.32519,11.16992-8.605a11.44643,11.44643,0,0,1,10.77807,6.27686h0a15.62089,15.62089,0,0,1,.35694,13.77051l-23.417,51.21045-18.61621,45.08349A4.49771,4.49771,0,0,1,802.08818,557.21623Z" transform="translate(-284.2586 -153.02954)" fill="#3f3d56"/><path d="M875.258,419.16911l-13.64656.24261a9.07354,9.07354,0,0,1-8.89589-11.58969,21.1284,21.1284,0,0,0,.65552-3.01274,15.22429,15.22429,0,0,0,.08977-3.35353,4.952,4.952,0,0,0-9.55443-1.40837v0c-2.2946.03268-7.18294-.71535-9.47754-.68266-4.87207-12.48981,5.7449-28.83323,17.17381-34.97183,11.65127-6.258,26.77522.1087,31.2414,13.15168,6.19838.11141,11.23461,6.22466,12.0334,13.1063s-2.03239,14.06747-6.36329,19.3418S878.49669,419.11153,875.258,419.16911Z" transform="translate(-284.2586 -153.02954)" fill="#2f2e41"/><path d="M830.4,730.69133a4.51452,4.51452,0,0,1-4.46143-4.00976l-5.06347-170.23536,63.78735,4.54053.04907.41016c14.4148,120.6626,9.48731,162.43164,9.43579,162.83935a4.49829,4.49829,0,0,1-5.07544,4.20264l-14.09667.33789a4.49788,4.49788,0,0,1-3.989-4.2959l-13.17139-123.2998a1.40643,1.40643,0,0,0-1.46606-1.05615,1.46264,1.46264,0,0,0-1.43921,1.17724l-5.08862,123.70361a4.48067,4.48067,0,0,1-4.04126,4.67041l-14.93237.99268A4.45633,4.45633,0,0,1,830.4,730.69133Z" transform="translate(-284.2586 -153.02954)" fill="#2f2e41"/><path d="M856.86846,576.787c-.3816,0-.76246-.00585-1.145-.01757-18.3418-.55225-32.69165-14.4292-36.65259-18.66944a4.47811,4.47811,0,0,1-1.0813-4.09717l10.5813-44.76416-2.80737-38.917a38.36931,38.36931,0,0,1,10.50561-29.6333,31.66353,31.66353,0,0,1,24.38648-9.86572c17.855.85205,31.9414,16.81152,32.0686,36.33252.19751,30.23486-.69263,32.312-.98486,32.99463-8.91089,20.79687-4.04419,49.98926-2.34034,58.4414a4.51639,4.51639,0,0,1-1.33715,4.1875C878.26152,572.07756,867.77178,576.78655,856.86846,576.787Z" transform="translate(-284.2586 -153.02954)" fill="#3f3d56"/><path d="M902.93315,565.40813a4.49659,4.49659,0,0,1-4.38037-3.49414L887.636,514.35686l-14.63061-54.35742a15.62106,15.62106,0,0,1,2.6272-13.52246,11.45551,11.45551,0,0,1,11.6665-4.41016c4.72876,1.07617,8.40527,5.03516,9.595,10.33252l11.95483,53.229,5.96241,53.94092a4.50859,4.50859,0,0,1-3.96265,4.96484l-7.3999.84424A4.48738,4.48738,0,0,1,902.93315,565.40813Z" transform="translate(-284.2586 -153.02954)" fill="#3f3d56"/><path d="M315.0904,570.53683a10.74268,10.74268,0,0,0,1.58187-16.3965l4.16719-93.01794-21.21552,2.38131,1.23255,90.98468a10.80091,10.80091,0,0,0,14.23391,16.04845Z" transform="translate(-284.2586 -153.02954)" fill="#ffb8b8"/><polygon points="69.534 574.966 81.609 577.089 93.543 531.525 77.722 528.392 69.534 574.966" fill="#ffb8b8"/><path d="M350.23234,727.314h38.53073a0,0,0,0,1,0,0v14.88687a0,0,0,0,1,0,0H365.1192A14.88686,14.88686,0,0,1,350.23234,727.314v0A0,0,0,0,1,350.23234,727.314Z" transform="translate(321.93567 1369.36466) rotate(-170.02922)" fill="#2f2e41"/><polygon points="36.392 581.01 48.652 581.01 54.484 533.722 36.39 533.723 36.392 581.01" fill="#ffb8b8"/><path d="M318.02393,730.53638h38.53073a0,0,0,0,1,0,0v14.88687a0,0,0,0,1,0,0H332.91078a14.88686,14.88686,0,0,1-14.88686-14.88686v0a0,0,0,0,1,0,0Z" transform="translate(390.35367 1322.9147) rotate(179.99738)" fill="#2f2e41"/><path d="M372.8035,721.09043a4.74805,4.74805,0,0,1-.57252-.0339l-14.43-1.1874a4.88077,4.88077,0,0,1-4.24251-5.65951l13.32468-74.681-9.00352-47.474a1.62706,1.62706,0,0,0-3.219.15995L343.40488,718.84227a4.92368,4.92368,0,0,1-5.2096,4.43715l-13.59479-.50631a4.88784,4.88784,0,0,1-4.53645-4.631l-.91385-151.76761,70.48116-8.80969,4.9236,76.04058-.01959.0805-16.99071,83.675A4.88583,4.88583,0,0,1,372.8035,721.09043Z" transform="translate(-284.2586 -153.02954)" fill="#2f2e41"/><circle cx="58.12912" cy="223.25508" r="24.56103" fill="#ffb8b8"/><path d="M365.53024,577.46685a20.11,20.11,0,0,1-10.85692-3.10569c-11.89736-7.43585-25.41059-4.48058-32.40686-2.057a4.88012,4.88012,0,0,1-4.22053-.48089,4.81086,4.81086,0,0,1-2.2244-3.55163L303.099,454.64609c-2.132-19.03768,9.33586-36.93669,27.2677-42.55965h0q1.01052-.317,2.05519-.60112a39.56862,39.56862,0,0,1,32.972,5.72253,40.20353,40.20353,0,0,1,17.1668,29.35308L393.27115,560.948a4.80738,4.80738,0,0,1-1.52715,4.0071C387.98953,568.42837,377.09235,577.46579,365.53024,577.46685Z" transform="translate(-284.2586 -153.02954)" fill="#875a7b"/><path d="M326.78912,479.0123l-28.70337-3.156a5.71747,5.71747,0,0,1-4.90543-7.13382l7.30606-27.84638a15.87852,15.87852,0,0,1,31.55638,3.56327l1.08461,28.67531a5.71749,5.71749,0,0,1-6.33825,5.89758Z" transform="translate(-284.2586 -153.02954)" fill="#875a7b"/><path d="M393.15631,566.55375a10.74269,10.74269,0,0,0-.40564-16.46764l-7.07293-92.84221-20.78851,4.67965,12.20288,90.41406a10.80091,10.80091,0,0,0,16.0642,14.21614Z" transform="translate(-284.2586 -153.02954)" fill="#ffb8b8"/><path d="M356.91916,473.17592a5.71132,5.71132,0,0,1-1.81845-4.39984l1.08461-28.67531a15.87852,15.87852,0,0,1,31.55638-3.56327l7.30606,27.84638a5.71747,5.71747,0,0,1-4.90543,7.13382l-28.70337,3.156A5.71106,5.71106,0,0,1,356.91916,473.17592Z" transform="translate(-284.2586 -153.02954)" fill="#875a7b"/><path d="M340.92691,401.771a5.683,5.683,0,0,1-1.29663-.15137l-.12475-.03028c-21.59449-3.30371-26.3667-15.81152-27.41431-21.03515-1.08423-5.4082.15039-10.62842,2.94019-12.65576-1.521-4.80274-1.27686-9.061.72729-12.66211,3.49536-6.28028,11.08106-8.40381,12.09839-8.66358,6.05811-4.46924,13.3064-1.48584,14.62524-.88086,11.71851-4.33545,16.19751-.72656,17.00757.07911,5.23828.94091,8.43115,2.96435,9.49121,6.01562,1.991,5.731-4.30542,12.85986-4.57446,13.16064l-.13965.15577-9.38013.44677a6.358,6.358,0,0,0-5.9812,7.3169h0a29.60406,29.60406,0,0,0,.96045,3.35547c1.602,5.00634,2.80225,9.2832,1.25415,10.90918a2.50966,2.50966,0,0,1-2.62524.45507c-1.46655-.3916-2.4624-.30957-2.9585.24463-.77026.85938-.53515,3.03467.66211,6.12549a5.73888,5.73888,0,0,1-1.0459,5.84717A5.56805,5.56805,0,0,1,340.92691,401.771Z" transform="translate(-284.2586 -153.02954)" fill="#2f2e41"/><path d="M425.2586,746.97046h-140a1,1,0,0,1,0-2h140a1,1,0,1,1,0,2Z" transform="translate(-284.2586 -153.02954)" fill="#ccc"/><path d="M913.2586,746.97046h-140a1,1,0,0,1,0-2h140a1,1,0,1,1,0,2Z" transform="translate(-284.2586 -153.02954)" fill="#ccc"/><path d="M712.97125,577.02954h-242a35.03979,35.03979,0,0,1-35-35v-354a35.03979,35.03979,0,0,1,35-35h242a35.03979,35.03979,0,0,1,35,35v354A35.03979,35.03979,0,0,1,712.97125,577.02954Z" transform="translate(-284.2586 -153.02954)" fill="#fff"/><path d="M674.97161,434.059h-166c-16.957-.08167-17.02751-25.9115.00084-25.99995l165.99916-.00005C691.91667,408.13842,692.0085,433.97026,674.97161,434.059Z" transform="translate(-284.2586 -153.02954)" fill="#ccc"/><path d="M674.97161,226h-166c-16.957-.08168-17.02751-25.91151.00084-25.99995L674.97161,200C691.91667,200.07936,692.0085,225.91121,674.97161,226Z" transform="translate(-284.2586 -153.02954)" fill="#ccc"/><path d="M674.97161,482.059h-166c-16.957-.08167-17.02751-25.9115.00084-25.99995l165.99916-.00005C691.91667,456.13842,692.0085,481.97026,674.97161,482.059Z" transform="translate(-284.2586 -153.02954)" fill="#ccc"/><path d="M674.97161,530.059h-166c-16.957-.08167-17.02751-25.9115.00084-25.99995l165.99916-.00005C691.91667,504.13842,692.0085,529.97026,674.97161,530.059Z" transform="translate(-284.2586 -153.02954)" fill="#ccc"/><path d="M671.97119,376.85885h-160a16.51868,16.51868,0,0,1-16.5-16.5V270.75924a16.51867,16.51867,0,0,1,16.5-16.5h160a16.51866,16.51866,0,0,1,16.5,16.5v89.59961A16.51867,16.51867,0,0,1,671.97119,376.85885Z" transform="translate(-284.2586 -153.02954)" fill="#875a7b"/><path d="M712.97125,577.02954h-242a35.03979,35.03979,0,0,1-35-35v-354a35.03979,35.03979,0,0,1,35-35h242a35.03979,35.03979,0,0,1,35,35v354A35.03979,35.03979,0,0,1,712.97125,577.02954Zm-242-418a29.03284,29.03284,0,0,0-29,29v354a29.03284,29.03284,0,0,0,29,29h242a29.03276,29.03276,0,0,0,29-29v-354a29.03276,29.03276,0,0,0-29-29Z" transform="translate(-284.2586 -153.02954)" fill="#e6e6e6"/></svg>
            </div>
            <div class="py-3">
                <form class="form-group" @submit.prevent="submitForm">
                    <div class="form_buttons" v-if="appraisalData.value.metaInfo.hasCurrentComponentAccess">
                        <button type="button" class="btn btn-secondary text-white" @click="changeReadOnlyMode" v-if="!disableButton">{{ editButtonText }}</button>
                        <button  class="btn btn-secondary text-white" :disabled="disableButton" v-if="!readOnlyMode">{{ buttonText }}</button>
                    </div>
                    <div class="row bg-white font-wieght-bold">
                        <div class="col-lg-1 border-grey headr border py-1 px-2" >No.</div>
                        <div class="col-lg-3 border-grey headr border py-1 px-2" >
                            <strong>Review Date</strong>
                        </div>
                        <div class="col-lg-6 border-grey headr border py-1 px-2" >
                            <strong>Review Notes</strong>
                        </div>
                        <div class="col-lg-2 border-grey headr border py-1 px-2" >
                            <strong>Creteria</strong>
                        </div>
                    </div>
                    
                    <template v-for="(review, key, index) in formData.set_reviews" :key="index">
                        <div class="row">
                            <div class="col-lg-1 border odoo-cell-grey p-0">
                                <div class="full_height_div  small_text">{{ index+1 }}</div>
                            </div>
                            <div class="col-lg-3 odoo-cell-grey border p-0">
                                <input v-if="appraisalData.value.state == 'planning' && review.finalized == false " class="form-control full_height_input" style="font-size: 12px" type="date" :disabled="readOnlyMode" v-model="formData.set_reviews['review_'+index].review_date"/>
                                <div v-else="" class="full_height_div small_text text-muted">{{ formData.set_reviews['review_'+index].review_date }}</div>
                            </div>
                            <div class="col-lg-6 odoo-cell-grey p-0">
                                <textarea v-if="appraisalData.value.state != 'planning'" class="form-control full_height_input small_text" rows="2" placeholder="Example - Outlook training completed on (insert date), daily to do lists being written. Responding to emails faster, but further improvement needed. Work shadowing will continue. Review in 2 Weeks." 
                                    :disabled="readOnlyMode" v-model="formData.set_reviews['review_'+index].notes"></textarea>
                                <div v-else="" class="full_height_div small_text text-muted">{{ formData.set_reviews['review_'+index].notes }}</div>
                            </div>
                            <div class="col-lg-2 odoo-cell-grey p-0">
                                <select v-if="appraisalData.value.state != 'planning'" class="form-control full_height_input small_text" :disabled="readOnlyMode" v-model="formData.set_reviews['review_'+index].result">
                                    <option value=""></option>
                                    <option value="met">Met</option>
                                    <option value="not_met">Not Met</option>
                                    <option value="partially_met">Partially Met</option>
                                </select>
                                <div v-else="" class="full_height_div small_text text-muted">{{creteriaDict[formData.set_reviews['review_'+index].result]}}</div>
                            </div>
                        </div>
                    </template>
                    <a href="#" class="btn-odoo" style="font-size: 14px;background: #875a7b;color: white;padding: 4px 12px;float: right;" @click.prevent="total_list_reviews_length++" v-if="!readOnlyMode && appraisalData.value.state == 'planning'">Add Line</a>
                </form>
            </div>
        </div>
    `,
}



// <label class="custom_label_style number_label" :for="['review_'+review.id]">{{index+1}}</label>
// <div class="row">
//     <div class="col-lg-6">
//         <label class="custom_label_style w-100 text-center" :for="['review_p1_'+review.id]">Performance Concern</label>
//         <small class="text-muted d-block">Detail specific dates and examples of where the standards have not been met.</small>
//         <textarea class="form-control mb-3" rows="4" placeholder="Example - Two deadlines missed (insert details) and complaint received from Department X who did not receive a response to an email sent twice on (insert dates" 
//             :id="['review_p1_'+review.id]" :disabled="readOnlyMode" v-model="formData.set_reviews['review_'+index].review_date"></textarea>
//     </div>
//     <div class="col-lg-6">
//         <label class="custom_label_style w-100 text-center" :for="['review_p3_'+review.id]">result</label>
//         <small class="text-muted d-block">Detail what has been agreed in terms of result required to achieve the expected standard of performance.</small>
//         <textarea class="form-control mb-3" rows="4" placeholder="Example - Operate daily ‘To Do’ check list and a diary. To respond to emails received within 3 working days. " 
//             :id="['review_p3_'+review.id]" :disabled="readOnlyMode"  v-model="formData.set_reviews['review_'+index].result"></textarea>
//     </div>
//     <div class="col-lg-12">
//         <label class="custom_label_style w-100 text-center" :for="['review_p2_'+review.id]">Agreed Improvement Action</label>
//         <small class="text-muted d-block">
//             Detail what is expected of the employee in terms of their performance i.e. what does ‘good’ look like.
//         </small>
//         <textarea class="form-control mb-3" rows="4" placeholder="Example - To effectively manage workload daily, meet deadlines efficiently, prioritize tasks and respond to emails in a timely manner. Measured by management observation of performance of tasks." 
//             :id="['review_p2_'+review.id]" :disabled="readOnlyMode" v-model="formData.set_reviews['review_'+index].notes"></textarea>
//     </div>
// </div>