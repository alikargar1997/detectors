# http://www.fileformat.info/info/unicode/block/arabic/list.htm
# -*- coding: utf-8 -*-

class PersianNormalizer:

     def __init__(self):
          self.__LoadCharactersDictionary()

     def clean_sentence(self, text):
          normalized_text = []
          if text is None:
               return ""
# -========================================  replace char in all text ===========================================
          text = text.replace('“', '"')     #جایگزین کردن تمام  “ با "
          text = text.replace('”', '"') #جایگزین کردن تمام  ” با "
          # text = self.name.replace('ىء', 'ء')#جایگزین کردن تمام  ىء با ء

          for c in text:
                    # print(c)
                    # if c =="٬" or  c =='،'  or c == ',':    # change  ,  and ٬  and ، in numbers and date
                    #     # print("----",c)
                    #     c_index=self.name.index(c)
                    #     # print("c=>",c_index)
                    #     # print(type(self.name[c_index + 1]))
                    #     if self.name[c_index-1].isdigit() :
                    #          try:    # add for edit  date with space:  17, 2018
                    #               # print(type(self.name[c_index+1]))
                    #               if self.name[c_index+1].isdigit():
                    #                   # print("dig =>",self.name[c_index+1])
                    #                   continue
                    #          except:
                    #               print("except Normalizer Digit")
                    #               continue


#=================== evaluate end char of each word for  TEH_MARBUTA and replace with HEH ======================
                    if c == self.__TEH_MARBUTA:    #if c == item[-1] and c == HEH:
                         normalized_text.append(self.__HEH)
                    # ----------------------------- DAL  -----------------------------------------------------
                    elif c == self.__ARABIC_LETTER_DDAL or c == self.__ARABIC_LETTER_DAL_WITH_RING \
                              or c == self.__ARABIC_LETTER_DAL_WITH_DOT_BELOW \
                              or c == self.__ARABIC_LETTER_DAL_WITH_DOT_BELOW_AND_SMALL_TAH \
                              or c == self.__ARABIC_LETTER_DAHAL or c == self.__ARABIC_LETTER_DDAHAL \
                              or c == self.__ARABIC_LETTER_DUL or c == self.__ARABIC_LETTER_DAL_WITH_THREE_DOTS_ABOVE_DOWNWARDS \
                              or c == self.__ARABIC_LETTER_DAL_WITH_THREE_DOTS_ABOVE_DOWNWARDS \
                              or c == self.__ARABIC_LETTER_DAL_WITH_FOUR_DOTS_ABOVE:
                         normalized_text.append(self.__ARABIC_LETTER_DAL)
                    # ----------------------------- REH -------------------------------------------------------
                    elif c == self.__ARABIC_LETTER_RREH or c == self.__ARABIC_LETTER_REH_WITH_SMALL_V \
                              or c == self.__ARABIC_LETTER_REH_WITH_RING or c == self.__ARABIC_LETTER_REH_WITH_DOT_BELOW \
                              or c == self.__ARABIC_LETTER_REH_WITH_SMALL_V_BELOW or c == self.__ARABIC_LETTER_REH_WITH_DOT_BELOW_AND_DOT_ABOVE \
                              or c == self.__ARABIC_LETTER_REH_WITH_TWO_DOTS_ABOVE:
                              normalized_text.append(self.__ARABIC_LETTER_REH)
                    # ------------------------------ SEEN   --------------------------------------------------
                    elif c == self.__ARABIC_LETTER_SEEN_WITH_THREE_DOTS_BELOW \
                              or c == self.__ARABIC_LETTER_SEEN_WITH_DOT_BELOW_AND_DOT_ABOVE:
                              normalized_text.append(self.__ARABIC_LETTER_SEEN)
                    # ---------------------------- YEH-------------------------------------------------------
                    elif c == self.__ARABIC_LETTER_YEH_WITH_HAMZA_ABOVE or c== self.__DottedYEH or c == self.__DOTLESS_YEH1 \
                             or c == self.__ARABIC_LETTER_KASHMIRI_YEH \
                             or c == self.__ARABIC_LETTER_FARSI_YEH_WITH_INVERTED_V \
                             or c == self.__ARABIC_LETTER_FARSI_YEH_WITH_TWO_DOTS_ABOVE \
                             or c == self.__ARABIC_LETTER_FARSI_YEH_WITH_THREE_DOTS_ABOVE \
                             or c == self.__ARABIC_LETTER_HIGH_HAMZA_YEH:
                            normalized_text.append(self.__DOTLESS_YEH2)
                    # ----------------------------_KAF--------------------------------------------------------
                    elif c == self.__ARABIC_KAF \
                             or c == self.__ARABIC_LETTER_KEHEH_WITH_TWO_DOTS_ABOVE \
                             or c == self.__ARABIC_LETTER_KEHEH_WITH_THREE_DOTS_BELOW \
                             or c == self.__ARABIC_LETTER_SWASH_KAF \
                             or c == self.__ARABIC_LETTER_KAF_WITH_RING \
                             or c == self.__ARABIC_LETTER_KAF_WITH_DOT_ABOVE \
                             or c == self.__ARABIC_LETTER_NG \
                             or c == self.__ARABIC_LETTER_KAF_WITH_THREE_DOTS_BELOW:
                           normalized_text.append(self.__ARABIC_KEHEH)
                    # ----------------------------- GAF ------------------------------------------------------
                    elif c == self.__ARABIC_LETTER_GAF_WITH_RING \
                              or c == self.__ARABIC_LETTER_NGOEH \
                              or c == self.__ARABIC_LETTER_GAF_WITH_TWO_DOTS_BELOW \
                              or c == self.__ARABIC_LETTER_GUEH \
                              or c == self.__ARABIC_LETTER_GAF_WITH_THREE_DOTS_ABOVE:  # print("c=", "ARABIC_GAF Replace with ARABIC_KAF: ",ARABIC_KAF)
                              normalized_text.append(self.__ARABIC_LETTER_GAF)
                    # ----------------------------- LAM ------------------------------------------------------
                    elif c == self.__ARABIC_LETTER_LAM_WITH_SMALL_V \
                              or c == self.__ARABIC_LETTER_LAM_WITH_DOT_ABOVE \
                              or c == self.__ARABIC_LETTER_LAM_WITH_THREE_DOTS_ABOVE \
                              or c == self.__ARABIC_LETTER_LAM_WITH_THREE_DOTS_BELOW:
                              normalized_text.append(self.__ARABIC_LETTER_LAM)
                    # ------------------------------- BEH ----------------------------------------------------
                    elif c == self.__ARABIC_LETTER_DOTLESS_BEH:
                              normalized_text.append(self.__ARABIC_LETTER_BEH)
                     # ----------------------------- ALEF -----------------------------------------------------
                    elif c == self.__ARABIC_LETTER_ALEF_WITH_HAMZA_ABOVE or c == self.__ARABIC_LETTER_ALEF_WITH_MADDA_ABOVE \
                             or c == self.__ARABIC_LETTER_ALEF_WITH_HAMZA_ABOVE \
                             or c == self.__RABIC_LETTER_ALEF_WITH_HAMZA_BELOW \
                             or c == self.__ARABICـLETTERـALEFـWASLA \
                             or c == self.__ARABIC_LETTER_ALEF_WITH_WAVY_HAMZA_ABOVE \
                             or c == self.__ARABIC_LETTER_ALEF_WITH_WAVY_HAMZA_BELOW:
                             normalized_text.append(self.__ARABIC_LETTER_ALEF)
                    # ----------------------------- NOON -----------------------------------------------------
                    elif c == self.__ARABIC_LETTER_NOON_WITH_DOT_BELOW \
                             or c == self.__ARABIC_LETTER_NOON_GHUNNA \
                            or c == self.__ARABIC_LETTER_RNOON or c == self.__ARABIC_LETTER_NOON_WITH_RING \
                            or c == self.__ARABIC_LETTER_NOON_WITH_THREE_DOTS_ABOVE:
                            normalized_text.append(self.__ARABIC_LETTER_NOON)
                    # ---------------------------- HAH  -------------------------------------------------------
                    elif c == self.__ARABIC_LETTER_HAH_WITH_HAMZA_ABOVE or c == self.__ARABIC_LETTER_HAH_WITH_TWO_DOTS_VERTICAL_ABOVE:
                            normalized_text.append(self.__ARABIC_LETTER_HAH)

                    # ===================================================================
                    elif c == self.__EM_QUAD or c == self.__EN_SPACE or c == self.__EM_SPACE  \
                           or c== self.__THREE_PER_EM_SPACE or c == self.__FOUR_PER_EM_SPACE \
                           or c == self.__SIX_PER_EM_SPACE or c== self.__FIGURE_SPACE \
                           or c==self.__THIN_SPACE or c== self.__NARROW_NO_BREAK_SPACE or c == self.__MEDIUM_MATHEMATICAL_SPACE :
                           normalized_text.append(self.__EN_QUAD)
                    # --------------------------- Half-space -------------------------------------------------
                    elif c == self.__HAIR_SPACE  or c == self.__ZERO_WIDTH_NON_JOINER:
                           normalized_text.append(self.__PUNCTUATION_SPACE)
                     # ---------------------------- DASH  -----------------------------------------------------
                    elif c == self.__FIGURE_DASH or c == self.__EM_DASH:
                           normalized_text.append(self.__EN_DASH)
                     # ---------------------------- HYPHEN ----------------------------------------------------
                    elif c == self.__NON_BREAKING_HYPHEN:
                           normalized_text.append(self.__HYPHEN)
                     # ---------------------------- WAW -------------------------------------------------------
                    elif c == self.__ARABIC_LETTER_WAW_WITH_HAMZA_ABOVE or c== self.__ARABIC_LETTER_HIGH_HAMZA_WAW \
                                    or c == self.__ARABIC_LETTER_WAW_WITH_RING \
                                    or c == self.__ARABIC_LETTER_WAW_WITH_TWO_DOTS_ABOVE \
                                    or c == self.__ARABIC_LETTER_WAW_WITH_DOT_ABOVE:
                                    normalized_text.append(self.__ARABIC_LETTER_WAW)
                    # ---------------------------- Evaluate Ereb  AND Skip -----------------------------------
                    elif c == self.__TATWEEL or c == self.__FATHATAN or c == self.__DAMMATAN or c == self.__KASRATAN \
                                    or c == self.__FATHA or c == self.__DAMMA or c == self.__ARABIC_KASRA or c == self.__arial_unic \
                                    or c == self.__SHADDA or c == self.__SUKUN or c == self.__ARABIC_HAMZA_ABOVE or c == self.__ARABIC_HAMZA_BELOW \
                                    or c == self.__ARABIC_SUBSCRIPT_ALEF or c == self.__ARABIC_INVERTED_DAMMA or c == self.__ARABIC_MARK_NOON_GHUNNA \
                                    or c == self.__ARABIC_VOWEL_SIGN_SMALL_V_ABOVE or c == self.__ARABIC_VOWEL_SIGN_INVERTED_SMALL_V_ABOVE \
                                    or c == self.__ARABIC_VOWEL_SIGN_DOT_BELOW or c == self.__ARABIC_REVERSED_DAMMA or c == self.__ARABIC_FATHA_WITH_TWO_DOTS \
                                    or c == self.__ARABIC_WAVY_HAMZA_BELOW or c == self.__ARABIC_LETTER_SUPERSCRIPT_ALEF or c == self.__ARABIC_LETTER_HIGH_HAMZA_ALEF \
                                    or c == self.__ARABIC_FULL_STOP or c == self.__ARABIC_SMALL_LOW_MEEM or c == self.__ARABIC_EMPTY_CENTRE_HIGH_STOP \
                                    or c == self.__ARABIC_SMALL_HIGH_NOON or c == self.__ARABIC_SMALL_HIGH_YEH or c == self.__ARABIC_SMALL_WAW or c == self.__ARABIC_SMALL_HIGH_MADDA \
                                    or c == self.__ARABIC_SMALL_LOW_SEEN or c == self.__ARABIC_SMALL_HIGH_MEEM_ISOLATED_FORM or c == self.__ARABIC_SMALL_HIGH_DOTLESS_HEAD_OF_KHAH \
                                    or c == self.__ARABIC_SMALL_HIGH_UPRIGHT_RECTANGULAR_ZERO or c == self.__ARABIC_SMALL_HIGH_THREE_DOTS or c == self.__ARABIC_SMALL_HIGH_MEEM_INITIAL_FORM \
                                    or c == self.__ARABIC_SMALL_HIGH_LIGATURE_QAF_WITH_LAM_WITH_ALEF_MAKSURA or c == self.__ARABIC_SMALL_HIGH_LIGATURE_SAD_WITH_LAM_WITH_ALEF_MAKSURA \
                                    or c == self.__ARABIC_SHADDA or c == self.__ARABIC_SMALL_HIGH_JEEM or c== self.__ARABIC_EMPTY_CENTRE_LOW_STOP or c == self.__ARABIC_SMALL_HIGH_LAM_ALEF\
                                    or c == self.__ARABIC_SMALL_FATHA  or c == self.__ARABIC_SMALL_HIGH_ZAIN  or c== self.__ARABIC_SMALL_HIGH_LIGATURE_ALEF_WITH_LAM_WITH_YEH \
                                    or c == self.__ARABIC_SMALL_HIGH_TAH  or c == self.__ARABIC_SIGN_TAKHALLUS or c == self.__ARABIC_SIGN_RADI_ALLAHOU_ANHU  or c == self.__ARABIC_SIGN_RAHMATULLAH_ALAYHE \
                                    or c == self.__ARABIC_SIGN_ALAYHE_SSALLAM  or c == self.__ARABIC_SIGN_SALLALLAHOU_ALAYHE_WASSALLAM  or c == self.__ARABIC_SIGN_MISRA \
                                    or c == self.__ARABIC_POETIC_VERSE_SIGN  or c== self.__ARABIC_DATE_SEPARATOR  or c ==  self.__AFGHANI_SIGN  or c == self.__ARABIC_RAY or c == self.__ARABIC_NUMBER_MARK_ABOVE \
                                    or c == self.__ARABIC_SIGN_SAMVAT  or c == self.__ARABIC_SIGN_SAFHA  or c == self.__ARABIC_FOOTNOTE_MARKER or c == self.__ARABIC_SIGN_SANAH  or c == self.__ARABIC_NUMBER_SIGN  \
                                    or c == self.__ZERO_WIDTH_SPACE or c == self.__ZERO_WIDTH_JOINER or c == self.__LEFT_TO_RIGHT_OVERRIDE or c == self.__RIGHT_TO_LEFT_OVERRIDE  \
                                    or c == self.__POP_DIRECTIONAL_FORMATTING \
                                    or c == self.__LEFT_TO_RIGHT_MARK or  c == self.__RIGHT_TO_LEFT_MARK :
                              continue

                    # -----------------------convert English_Arabic_numbers to Persian_numbers ----------
                    elif c == self.__Ar_D0 or c == self.__EN_D0:
                         #print(c)
                         normalized_text.append(c.replace(c,self.__FA_D0))
                    elif c == self.__Ar_D1 or c == self.__EN_D1:
                         normalized_text.append(c.replace(c,self.__FA_D1))
                         #print(c)
                    elif c == self.__Ar_D2 or c == self.__EN_D2:
                         normalized_text.append(c.replace(c,self.__FA_D2))
                    elif c == self.__Ar_D3 or c == self.__EN_D3:
                         normalized_text.append(c.replace(c,self.__FA_D3))
                    elif c == self.__Ar_D4 or c == self.__EN_D4:
                         normalized_text.append(c.replace(c,self.__FA_D4))
                    elif c == self.__Ar_D5 or c == self.__EN_D5:
                         normalized_text.append(c.replace(c,self.__FA_D5))
                    elif c == self.__Ar_D6 or c == self.__EN_D6 :
                         normalized_text.append(c.replace(c,self.__FA_D6))
                    elif c == self.__Ar_D7 or c == self.__EN_D7:
                         normalized_text.append(c.replace(c,self.__FA_D7))
                    elif c == self.__Ar_D8 or c ==self.__EN_D8 :
                         normalized_text.append(c.replace(c,self.__FA_D8))
                    elif c == self.__Ar_D9 or c == self.__EN_D9:
                         normalized_text.append(c.replace(c,self.__FA_D9))
                    # =================================================================
                    elif c == "?":
                         c = "؟"
                         normalized_text.append(c)
                    else:
                         normalized_text.append(c)


          result = ''.join(normalized_text)
          # data={}
          # data["text"]=result
          return result


     def __LoadCharactersDictionary(self):
         # ================ Numbers ======================
         # Persian Numbers
         self.__FA_D0 = '\u06F0'
         self.__FA_D1 = '\u06F1'
         self.__FA_D2 = '\u06F2'
         self.__FA_D3 = '\u06F3'
         self.__FA_D4 = '\u06F4'
         self.__FA_D5 = '\u06F5'
         self.__FA_D6 = '\u06F6'
         self.__FA_D7 = '\u06F7'
         self.__FA_D8 = '\u06F8'
         self.__FA_D9 = '\u06F9'
         # Arabic Numbers
         self.__Ar_D0 = '\u0660'
         self.__Ar_D1 = '\u0661'
         self.__Ar_D2 = '\u0662'
         self.__Ar_D3 = '\u0663'
         self.__Ar_D4 = '\u0664'
         self.__Ar_D5 = '\u0665'
         self.__Ar_D6 = '\u0666'
         self.__Ar_D7 = '\u0667'
         self.__Ar_D8 = '\u0668'
         self.__Ar_D9 = '\u0669'
         # English Numbers
         self.__EN_D0 = '\u0030'
         self.__EN_D1 = '\u0031'
         self.__EN_D2 = '\u0032'
         self.__EN_D3 = '\u0033'
         self.__EN_D4 = '\u0034'
         self.__EN_D5 = '\u0035'
         self.__EN_D6 = '\u0036'
         self.__EN_D7 = '\u0037'
         self.__EN_D8 = '\u0038'
         self.__EN_D9 = '\u0039'
         # Mosavet Charecters
         # ---------------------  DAL  -----------------------------------
         self.__ARABIC_LETTER_DAL = u'\u062F'  # د
         self.__ARABIC_LETTER_DDAL = u'\u0688'  # ڈ
         self.__ARABIC_LETTER_DAL_WITH_RING = u'\u0689'  # ډ
         self.__ARABIC_LETTER_DAL_WITH_DOT_BELOW = u'\u068A'  # ڊ
         self.__ARABIC_LETTER_DAL_WITH_DOT_BELOW_AND_SMALL_TAH = u'\u068B'  # ڋ
         self.__ARABIC_LETTER_DAHAL = u'\u068C'  # ڌ
         self.__ARABIC_LETTER_DDAHAL = u'\u068D'  # ڍ
         self.__ARABIC_LETTER_DUL = u'\u068E'  # ڎ
         self.__ARABIC_LETTER_DAL_WITH_THREE_DOTS_ABOVE_DOWNWARDS = u'\u068F'  # ڏ
         self.__ARABIC_LETTER_DAL_WITH_FOUR_DOTS_ABOVE = u'\u0690'  # ڐ
         # -----------------------  REH ------------------------------------
         self.__ARABIC_LETTER_REH = u'\u0631'  # ر
         self.__ARABIC_LETTER_RREH = u'\u0691'  # ڑ
         self.__ARABIC_LETTER_REH_WITH_SMALL_V = 'u\u0692'  # ڒ
         self.__ARABIC_LETTER_REH_WITH_RING = u'\u0693'  # ړ
         self.__ARABIC_LETTER_REH_WITH_DOT_BELOW = u'\u0694'  # ڔ
         self.__ARABIC_LETTER_REH_WITH_SMALL_V_BELOW = u'\u0695'  # ڕ
         self.__ARABIC_LETTER_REH_WITH_DOT_BELOW_AND_DOT_ABOVE = u'\u0696'  # ږ
         self.__ARABIC_LETTER_REH_WITH_TWO_DOTS_ABOVE = u'\u0697'  # ڗ
         # ----------------------  SEEN  -----------------------------------
         self.__ARABIC_LETTER_SEEN = u'\u0633'  # س
         self.__ARABIC_LETTER_SEEN_WITH_THREE_DOTS_BELOW = u'\u069B'  # ڛ
         self.__ARABIC_LETTER_SEEN_WITH_DOT_BELOW_AND_DOT_ABOVE = u'\u069A'  # ښ
         # ---------------------  YEH  -----------------------------
         self.__DOTLESS_YEH2 = u'\u06cc'  # ی  == persian
         self.__DottedYEH = u'\u064A'  # ي
         self.__DOTLESS_YEH1 = u'\u0649'  # ى
         self.__ARABIC_LETTER_YEH_WITH_HAMZA_ABOVE = u'\u0626'  # ئ
         self.__ARABIC_LETTER_KASHMIRI_YEH = u'\u0620'  # ؠ
         self.__ARABIC_LETTER_FARSI_YEH_WITH_INVERTED_V = u'\u063D'  # ؽ
         self.__ARABIC_LETTER_FARSI_YEH_WITH_TWO_DOTS_ABOVE = u'\u063E'  # ؾ
         self.__ARABIC_LETTER_FARSI_YEH_WITH_THREE_DOTS_ABOVE = u'\063F'  # ؿ
         self.__ARABIC_LETTER_HIGH_HAMZA_YEH = u'\u0678'  # ٸ
         # ----------------------  KAF  ----------------------------
         self.__ARABIC_KAF = u'\u0643'  # ك
         self.__ARABIC_KEHEH = u'\u06A9'  # ک  persian
         self.__ARABIC_LETTER_KEHEH_WITH_TWO_DOTS_ABOVE = u'\u063B'  # ػ
         self.__ARABIC_LETTER_KEHEH_WITH_THREE_DOTS_BELOW = u'\u063C'  # ؼ
         self.__ARABIC_LETTER_SWASH_KAF = u'\u06AA'  # ڪ
         self.__ARABIC_LETTER_KAF_WITH_RING = u'\u06AB'  # ګ
         self.__ARABIC_LETTER_KAF_WITH_DOT_ABOVE = 'u\u06AC'  # ڬ
         self.__ARABIC_LETTER_NG = u'\u06AD'  # ڭ
         self.__ARABIC_LETTER_KAF_WITH_THREE_DOTS_BELOW = 'u\u06AE'  # ڮ
         # ---------------------  GAF -------------------------------
         self.__ARABIC_LETTER_GAF = u'\u06AF'  # گ persian
         self.__ARABIC_LETTER_GAF_WITH_RING = u'\u06B0'  # ڰ
         self.__ARABIC_LETTER_NGOEH = u'\u06B1'  # ڱ
         self.__ARABIC_LETTER_GAF_WITH_TWO_DOTS_BELOW = 'u\u06B2'  # ڲ
         self.__ARABIC_LETTER_GUEH = 'u\u06B3'  # ڳ
         self.__ARABIC_LETTER_GAF_WITH_THREE_DOTS_ABOVE = u'\u06B4'  # ڴ
         # ---------------------  LAM  ------------------------------
         self.__ARABIC_LETTER_LAM = u'\u0644'  # ل
         self.__ARABIC_LETTER_LAM_WITH_SMALL_V = u'\u06B5'  # ڵ
         self.__ARABIC_LETTER_LAM_WITH_DOT_ABOVE = u'\u06B6'  # ڶ
         self.__ARABIC_LETTER_LAM_WITH_THREE_DOTS_ABOVE = u'\u06B7'  # ڷ
         self.__ARABIC_LETTER_LAM_WITH_THREE_DOTS_BELOW = u'\u06B8'  # ڸ
         # --------------------  BEH  ---------------------
         self.__ARABIC_LETTER_DOTLESS_BEH = u'\u066E'  # ٮ
         self.__ARABIC_LETTER_BEH = u'\u0628'  # ب
         # -------------------- ALEF ---------------------------------
         self.__ARABIC_LETTER_ALEF = u'\u0627'  # ا
         self.__ARABIC_LETTER_ALEF_WITH_HAMZA_ABOVE = u'\u0623'  # أ
         self.__ARABIC_LETTER_ALEF_WITH_MADDA_ABOVE = u'\u0622'  # آ
         self.__ARABIC_LETTER_ALEF_WITH_HAMZA_ABOVE = u'\u0623'  # أ
         self.__RABIC_LETTER_ALEF_WITH_HAMZA_BELOW = u'\u0625'  # إ
         self.__ARABICـLETTERـALEFـWASLA = u'\u0671'  # ٱ
         self.__ARABIC_LETTER_ALEF_WITH_WAVY_HAMZA_ABOVE = u'\u0672'  # ٲ
         self.__ARABIC_LETTER_ALEF_WITH_WAVY_HAMZA_BELOW = u'\u0673'  # ٳ
         # --------------------- NOON  --------------------------------------------
         self.__ARABIC_LETTER_NOON = u'\u0646'  # ن
         self.__ARABIC_LETTER_NOON_WITH_DOT_BELOW = u'\u06B9'  # ڹ
         self.__ARABIC_LETTER_NOON_GHUNNA = u'\u06BA'  # ں
         self.__ARABIC_LETTER_RNOON = u'\u06BB'  # ڻ
         self.__ARABIC_LETTER_NOON_WITH_RING = u'\u06BC'  # ڼ
         self.__ARABIC_LETTER_NOON_WITH_THREE_DOTS_ABOVE = u'\u06BD'  # ڽ
         # ----------------------  ح HAH  --------------------
         self.__ARABIC_LETTER_HAH = u'\u062D'  # ح
         self.__ARABIC_LETTER_HAH_WITH_HAMZA_ABOVE = u'\u0681'  # ځ
         self.__ARABIC_LETTER_HAH_WITH_TWO_DOTS_VERTICAL_ABOVE = u'\u0682'  # ڂ
         # --------------------  WAW ---------------------------------
         self.__ARABIC_LETTER_WAW = u'\u0648'  # و
         self.__ARABIC_LETTER_WAW_WITH_HAMZA_ABOVE = u'\u0624'  # ؤ
         self.__ARABIC_LETTER_HIGH_HAMZA_WAW = u'\u0676'  # ٶ
         self.__ARABIC_LETTER_WAW_WITH_RING = u'\u06C4'  # ۄ
         self.__ARABIC_LETTER_WAW_WITH_TWO_DOTS_ABOVE = u'\u06CA'  # ۊ
         self.__ARABIC_LETTER_WAW_WITH_DOT_ABOVE = u'\u06CF'  # ۏ
         # =============================================
         self.__ARABIC_LETTER_HAMZA = u'\u0621'  # ء
         # ---------------------  HEH - TEH_MARBUTU  ------------------------------
         self.__TEH_MARBUTA = u'\u0629'  # TEH_MARBUTA: ة
         self.__HEH = u'\u0647'  # HEH=> ه
         # --------------------  ERAB -----------------------------------------
         self.__TATWEEL = u'\u0640'  # ـ
         self.__FATHATAN = u'\u064B'  # ً
         self.__DAMMATAN = u'\u064C'  # ٌ
         self.__KASRATAN = u'\u064D'  # ٍ
         self.__FATHA = u'\u064E'  # َ
         self.__DAMMA = u'\u064F'  # ُ
         self.__ARABIC_KASRA = u'\u0650'  # ِ
         self.__arial_unic = u'\u0650'  # ِ
         self.__SHADDA = u'\u0651'  # ّ
         self.__SUKUN = u'\u0652'  # ْ
         self.__ARABIC_SMALL_HIGH_ZAIN = u'\u0617'  # ؗ
         self.__ARABIC_SMALL_HIGH_LIGATURE_ALEF_WITH_LAM_WITH_YEH = u'\u0616'  # ؖ
         self.__ARABIC_SMALL_HIGH_TAH = u'\u0615'  # ؕ
         self.__ARABIC_SIGN_TAKHALLUS = u'\u0614'  # ؔ
         self.__ARABIC_SIGN_RADI_ALLAHOU_ANHU = u'\u0613'  # ؓ
         self.__ARABIC_SIGN_RAHMATULLAH_ALAYHE = u'\u0612'  # ؒ
         self.__ARABIC_SIGN_ALAYHE_SSALLAM = u'\u0611'  # ؑ
         self.__ARABIC_SIGN_SALLALLAHOU_ALAYHE_WASSALLAM = u'\u0610'  # ؐ
         self.__ARABIC_SIGN_MISRA = u'\u060F'  # ؏
         self.__ARABIC_POETIC_VERSE_SIGN = u'\u060E'  # ؎
         self.__ARABIC_DATE_SEPARATOR = u'\u060D'  # ؍
         self.__AFGHANI_SIGN = u'\u060B'  # ؋
         self.__ARABIC_RAY = u'\u0608'  # ؈
         self.__ARABIC_NUMBER_MARK_ABOVE = 'u\u0605'  # ؅
         self.__ARABIC_SIGN_SAMVAT = 'u\0604'  # ؄
         self.__ARABIC_SIGN_SAFHA = u'\0603'  # ؃
         self.__ARABIC_FOOTNOTE_MARKER = u'\u0602'  # ؂
         self.__ARABIC_SIGN_SANAH = u'\u0601'  # ؁
         self.__ARABIC_NUMBER_SIGN = u'\u0600'  # ؀
         self.__ARABIC_SMALL_FATHA = u'\u0618'  # ؘ
         self.__ARABIC_HAMZA_ABOVE = u'\u0654'  # ٔ
         self.__ARABIC_HAMZA_BELOW = u'\u0655'  # ٖ  ٕ
         self.__ARABIC_SUBSCRIPT_ALEF = u'\u0656'  #
         self.__ARABIC_INVERTED_DAMMA = u'\u0657'  # ٗ
         self.__ARABIC_MARK_NOON_GHUNNA = u'\u0658'  # ٘
         self.__ARABIC_VOWEL_SIGN_SMALL_V_ABOVE = u'\u065A'  # ٚ
         self.__ARABIC_VOWEL_SIGN_INVERTED_SMALL_V_ABOVE = u'\u065B'  # ٛ
         self.__ARABIC_VOWEL_SIGN_DOT_BELOW = u'\u065C'  # ٜ
         self.__ARABIC_REVERSED_DAMMA = u'\u065D'  # ٝ
         self.__ARABIC_FATHA_WITH_TWO_DOTS = u'\u065E'  # ٞ
         self.__ARABIC_WAVY_HAMZA_BELOW = u'\u065F'  # ٟ
         self.__ARABIC_LETTER_SUPERSCRIPT_ALEF = u'\u0670'  # ٰ
         self.__ARABIC_LETTER_HIGH_HAMZA_ALEF = u'\u0674'  # ٴ
         self.__ARABIC_FULL_STOP = 'u\u06D4'  # ۔
         self.__ARABIC_SMALL_LOW_MEEM = u'\u06ED'  # ۭ
         self.__ARABIC_EMPTY_CENTRE_HIGH_STOP = u'\u06EB'  # ۫
         self.__ARABIC_SMALL_HIGH_NOON = u'\u06E8'  # ۨ
         self.__ARABIC_SMALL_HIGH_YEH = u'\u06E7'  # ۧ
         self.__ARABIC_SMALL_WAW = u'\u06E5'  # ۥ
         self.__ARABIC_SMALL_HIGH_MADDA = u'\u06E4'  # ۤ
         self.__ARABIC_SMALL_LOW_SEEN = u'\u06E3'  # ۣ
         self.__ARABIC_SMALL_HIGH_MEEM_ISOLATED_FORM = u'\u06E2'  # ۢ
         self.__ARABIC_SMALL_HIGH_DOTLESS_HEAD_OF_KHAH = u'\u06E1'  # ۡ
         self.__ARABIC_SMALL_HIGH_UPRIGHT_RECTANGULAR_ZERO = u'\u06E0'  # ۠
         self.__ARABIC_SMALL_HIGH_THREE_DOTS = u'\u06DB'  # ۛ
         self.__ARABIC_SMALL_HIGH_MEEM_INITIAL_FORM = u'\u06D8'  # ۘ
         self.__ARABIC_SMALL_HIGH_LIGATURE_QAF_WITH_LAM_WITH_ALEF_MAKSURA = u'\u06D7'  # ۗ
         self.__ARABIC_SMALL_HIGH_LIGATURE_SAD_WITH_LAM_WITH_ALEF_MAKSURA = u'\u06D6'  # ۖ
         self.__ARABIC_SHADDA = u'\u0651'  # ّ

         self.__ARABIC_SMALL_HIGH_JEEM = u'\u06DA'  # ۚ

         self.__ARABIC_EMPTY_CENTRE_LOW_STOP = u'\u06EA'  # ۪

         self.__ARABIC_SMALL_HIGH_LAM_ALEF = u'\u06D9'
         #    ۙ
         # ------------------- SPACE  -----------------------------------------------
         self.__EN_QUAD = u'\u2000'  # SPACE
         self.__EM_QUAD = u'\u2001'  # SPACE
         self.__EN_SPACE = u'\u2002'  # #SPACE
         self.__EM_SPACE = u'\u2003'  # #SPACE
         self.__THREE_PER_EM_SPACE = u'\u2004'  # SPACE
         self.__FOUR_PER_EM_SPACE = u'\u2005'  # SPACE
         self.__SIX_PER_EM_SPACE = u'\u2006'  # SPACE
         self.__FIGURE_SPACE = u'\u2007'  # SPACE
         self.__THIN_SPACE = u'\u2009'  # SPACE
         self.__NARROW_NO_BREAK_SPACE = u'\u202F'  # SPACE
         self.__MEDIUM_MATHEMATICAL_SPACE = u'\u205F'  # SPACE

         self.__PUNCTUATION_SPACE = u'\u2008'  # نیم فاصله
         self.__HAIR_SPACE = u'\u200A'  # نیم فاصله
         self.__ZERO_WIDTH_NON_JOINER = u'\u200C'  # نیم فاصله

         # ============== REMOVE ===========================
         self.__ZERO_WIDTH_SPACE = u'\u200B'  # چسبان
         self.__ZERO_WIDTH_JOINER = u'\u200D'  # حذف میکنم    چسبان
         # ============================================
         self.__LEFT_TO_RIGHT_MARK = u'\u200E'
         self.__RIGHT_TO_LEFT_MARK = u'\u200F'
         self.__LEFT_TO_RIGHT_OVERRIDE = u'\u202D'
         self.__RIGHT_TO_LEFT_OVERRIDE = u'\u202E'
         self.__POP_DIRECTIONAL_FORMATTING = u'\u202C'
         # ------------------- HYPHEN -   ----------------------------------------------
         self.__HYPHEN = u'\u2010'
         self.__NON_BREAKING_HYPHEN = u'\u2011'
         # ------------------- DASH  –  ----------------------------------------------
         self.__FIGURE_DASH = u'\u2012'
         self.__EN_DASH = u'\u2013'
         self.__EM_DASH = u'\u2014'
